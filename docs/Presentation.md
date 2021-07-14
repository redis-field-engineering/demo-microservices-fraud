---
theme : "night"
transition: "convex"
title: "Anti Fraud with Redis"
highlightTheme: "darkula"
logoImg: "./redis-labs-header.png"
slideNumber: false
---

## Anti-Fraud with Redis

---

## Goals

- Minimize detection time

- Stop fraud as early as possible in the process

- Layer the approach for maximum efficiency 

- Only run computationally expensive calculations when absolutely necessary

---

## Flow

<img src="./flow.svg" style="background:none; border:none; box-shadow:none;">

---

## Fraud Score

| | |
|--|--|
|Identity|Confirm the user characteristics|
|Profile|Confirm the user behavior|
|AI|Score overall purchase patterns|
| | | 

---

## Architecture

<img src="./overall_arch.png" style="background:none; border:none; box-shadow:none;">

---

## Architecture

|Component|Usage|
|--|--|
|Redis Search | Catalog and Shopping Cart |
|Redis Bloom | User purchase profiles |
|Redis AI | Cart scoring |
|||

---

## Services - Identity

<br>

- Check user session (cookie)
- Check user IP address 
- Check user Browser fingerprint
- Score Identity 0.0-1.0

---

## Services - Profile

### Redis Bloom
<br>

- purchased from this category before?
- purchase from category and level before?
- Score Profile 0.0-1.0

---

## Services - AI

### Redis AI
<br>

- Market Basket Analysis
- to be avoided if possible
- Score AI 0.0-1.0

---

## Scoring

<small>

- Each stage checks the cumulative score
- If it exceeds 1.5 we consider it safe and proceed
- Unsafe scores in the cart require further action

</small>

---

## Services - Cart

### Redis Search
<br>

- stored in search by session
- rescore can be triggered

---

<img src="./guest_sequence.svg" style="background:none; border:none; box-shadow:none;">

---

<img src="./good_user_sequence.svg" style="background:none; border:none; box-shadow:none;">

---

<img src="./bad_user_sequence.svg" style="background:none; border:none; box-shadow:none;">

---

## Demo

Watch the fraud score!!