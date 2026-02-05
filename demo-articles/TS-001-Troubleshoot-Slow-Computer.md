---
id: TS-001
title: Troubleshoot Slow Computer Performance
category: Troubleshooting Guide
audience: End-User
domain: Windows
tags: slow, computer, performance, speed, lag, freeze, hang, startup, boot
priority: P1-CRITICAL
related_articles: []
last_updated: 2024-12-11
---

# Troubleshoot Slow Computer Performance

## When to Use This Article
Use this guide when your computer is running slowly, taking a long time to start up, freezing, or lagging during normal use.

## Symptoms
- Computer takes more than 2 minutes to boot up
- Applications take a long time to open
- Mouse cursor freezes or lags
- "Not Responding" messages appear frequently
- Typing has a delay before characters appear
- Videos stutter or buffer on local playback

## Quick Fixes (Try These First)

### Fix 1: Restart Your Computer
1. Save all your work
2. Click Start > Power > Restart
3. Wait for full restart (not Shut Down, use Restart)
4. Test performance after restart

**Why this works:** Clears memory and stops runaway processes

### Fix 2: Close Unnecessary Programs
1. Look at your taskbar for open applications
2. Right-click programs you're not using
3. Select "Close window"
4. Close browser tabs you don't need (each tab uses memory)

### Fix 3: Check for Windows Updates Installing
1. Click Start > Settings > Windows Update
2. If updates are installing, let them complete
3. Restart when prompted
4. Performance often improves after updates finish

## Diagnostic Steps

### Step 1: Check Task Manager
1. Press Ctrl + Shift + Esc to open Task Manager
2. Click "More details" if needed
3. Look at the Performance tab
4. Check these values:
   - **CPU:** Consistently above 80% = problem
   - **Memory:** Above 90% = problem
   - **Disk:** At 100% = problem

### Step 2: Identify Resource-Hungry Programs
1. In Task Manager, click the Processes tab
2. Click "CPU" column to sort by CPU usage
3. Note any program using more than 30% consistently
4. Click "Memory" column to sort by memory
5. Note any program using more than 2GB

### Step 3: Handle Problem Programs
If you identified a problem program:
1. Select the program in Task Manager
2. Click "End task" (save your work in that program first)
3. If it's a critical work program, report to IT

## Common Causes and Solutions

### Cause 1: Too Many Startup Programs
**Check:** Computer slow only at startup
**Solution:**
1. Open Task Manager > Startup tab
2. Look for programs with "High" impact
3. Right-click unnecessary programs > Disable
4. Keep enabled: antivirus, company-required software
5. Restart to test

### Cause 2: Low Disk Space
**Check:** Less than 10% free space on C: drive
**Solution:**
1. Open File Explorer
2. Right-click C: drive > Properties
3. Click "Disk Cleanup"
4. Check all boxes and click OK
5. Empty Recycle Bin
6. Delete files from Downloads folder you no longer need

### Cause 3: Too Many Browser Tabs
**Check:** Browser using high memory in Task Manager
**Solution:**
1. Close tabs you're not actively using
2. Bookmark pages to revisit later
3. Restart your browser
4. Consider a browser extension to manage tabs

### Cause 4: Antivirus Scanning
**Check:** Antivirus program high in Task Manager during slowdown
**Solution:**
1. Let the scan complete (important for security)
2. Schedule scans for lunch or after hours
3. Contact IT if scans run constantly

### Cause 5: Computer Needs Restart
**Check:** Computer has been on for days/weeks
**Solution:**
1. Restart at least once per week
2. Use "Restart" not "Shut Down" (Shut Down uses Fast Startup which doesn't fully clear memory)

## When to Contact IT

### Escalate if:
- Problem persists after trying all quick fixes
- Computer is more than 5 years old
- Task Manager shows hardware at 100% with few programs open
- You see error messages about memory or disk
- Computer crashes or blue screens
- Slowness started after a suspicious email or download

### Information to Provide IT:
- When did the slowness start?
- What programs are you trying to use?
- Screenshot of Task Manager Performance tab
- Any error messages you've seen

## Prevention Tips
- Restart your computer at least once a week
- Keep your Downloads folder clean
- Close programs when you're done with them
- Don't install unauthorized software
- Keep browser tabs to a reasonable number (under 20)

## Success Criteria
- Computer responds promptly to clicks and typing
- Applications open within a few seconds
- No "Not Responding" messages
- Task Manager shows CPU/Memory/Disk under 80% during normal use

## Related Articles
- HT-004: How to Clear Browser Cache
- TS-005: Troubleshoot Computer Crashes
- HT-015: How to Check Disk Space
