# TUNING — Assignment 6

All strips are **fixture captures**. Each is a preview scene rendered by Movie Maker at 30 fps, with a fixed seed set on the preview's own instance only. Setup: Godot 4.7.2, Forward+, NVIDIA GeForce RTX 3060 Laptop GPU, 1280 × 720.

Each revision below records five things:
- what I saw in the running game;
- Claude's reading of the strip before the change;
- the change itself, which I approved;
- Claude's prediction for the new strip, and its comparison of the new strip with that prediction;
- my verdict in the running game.

## 2026-11-06 — Effect A, r0 (first strip, before any tuning)

**Strip:** `captures/cover_hit_burst/r0/` — frames 10, 12, 15, 20, 30, 50 (fixture).

**Capture log:** `logs/capture_cover_hit_burst_r0.log`. It shows the device NVIDIA RTX 3060 Laptop, and one burst at frame 10 at (600.7, 349.15), rotation −π (pointing back out of the left face).

**My first look** (preview window, 1280 × 720, before any Claude read the strip), in my own words:

> 闪光看得见，正好。砖块主要往左侧飞，也不错。看得清，大小合适。大概一两秒没有了。

(English: The flash is visible and about right. The chips fly mainly to the left, which is good. It is readable and the size is right. It is gone after about one or two seconds.)

**My second look** (preview window, after viewing my own strip, before any Claude reading):

> 看得清。

(English: The chips are readable against the ground.)

Checked against the strip: the burst is gone by frame 50 (1.33 s) and only faint dust is left at frame 30 (0.67 s), so my "one or two seconds" overestimated the duration (brief R2.4).
