package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/go-redis/redis/v8"
)

var ctx = context.Background()

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return defaultValue
	}
	return value
}

func enhanceMessage(redisClient *redis.Client, ctx context.Context, outputStream string, message map[string]interface{}) error {
	score := 0.0
	if redisClient.SIsMember(ctx, fmt.Sprintf("Identity:%s:IPS", message["user"]), message["ipaddr"]).Val() {
		score += 1.0
	}
	if redisClient.SIsMember(ctx, fmt.Sprintf("Identity:%s:BrowserFingerprint", message["user"]), message["fingerprint"]).Val() {
		score += 1.0
	}

	message["identity_score"] = fmt.Sprintf("%.2f", score/2.0)
	// Remove the action so that we can set for the next stage
	delete(message, "action")
	xadderr := redisClient.XAdd(ctx, &redis.XAddArgs{
		Stream: outputStream,
		ID:     "*",
		Values: message,
	}).Err()

	if xadderr != nil {
		return fmt.Errorf("Error: %s Unable to enhance the message %+v", xadderr, message)
	}

	return nil

}

func updateIdentity(redisClient *redis.Client, ctx context.Context, message map[string]interface{}) error {
	err := redisClient.SAdd(ctx, fmt.Sprintf("Identity:%s:IPS", message["user"]), message["ipaddr"]).Err()
	if err != nil {
		return fmt.Errorf("Unable to update IPS: %s", err)
	}
	err = redisClient.SAdd(ctx, fmt.Sprintf("Identity:%s:BrowserFingerprint", message["user"]), message["fingerprint"]).Err()
	if err != nil {
		return fmt.Errorf("Unable to update BrowserFingerprint: %s", err)
	}
	return nil
}

func processMessage(redisClient *redis.Client, ctx context.Context, message map[string]interface{}, outputStream string) error {
	if myaction, ok := message["action"]; ok {
		switch myaction {
		case "enhance":
			enhanceMessage(redisClient, ctx, outputStream, message)
		case "update":
			err := updateIdentity(redisClient, ctx, message)
			if err != nil {
				return fmt.Errorf("Couldn't update Identitiey: %s", err)
			}
		default:
			return fmt.Errorf("Message has unknown action: %s", myaction)
		}
	} else {
		log.Println("Message has no action")
		return fmt.Errorf("Message has no action")
	}
	return nil
}

func main() {
	log.Println("Starting identity service")

	redisHost := getEnv("REDIS_HOST", "localhost")
	redisPort := getEnv("REDIS_PORT", "6379")
	redisPass := getEnv("REDIS_PASSWORD", "")
	inputStream := getEnv("REDIS_INPUT_STREAM", "identity")
	outputStream := getEnv("REDIS_OUTPUT_STREAM", "profile")

	client := redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%s", redisHost, redisPort),
		Password:     redisPass,
		MinIdleConns: 2,
		MaxConnAge:   0,
		MaxRetries:   10,
	})

	client.XGroupCreateMkStream(ctx, inputStream, "IDENTITY-GROUP", "0").Err()
	for {
		res, _ := client.XReadGroup(ctx, &redis.XReadGroupArgs{
			Group:    "IDENTITY-GROUP",
			Consumer: "IDENTITY-CONSUMER",
			Streams:  []string{inputStream, ">"},
			Count:    1,
			Block:    200 * time.Millisecond,
		}).Result()
		for _, x := range res {
			for _, y := range x.Messages {
				kvs := map[string]interface{}{
					fmt.Sprintf("%s-ID", inputStream): y.ID,
				}
				for k, v := range y.Values {
					kvs[k] = v
				}
				err := processMessage(client, ctx, kvs, outputStream)
				if err != nil {
					log.Printf("Unable to process message: %s : %s", y.ID, err)
				}
			}
		}
	}
}
