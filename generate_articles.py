"""
TactivAI KB Article Generator
===============================
Uses OpenAI GPT to generate real-content KB articles from a list of topics.

Run:  python generate_articles.py

You will be prompted for your OpenAI API Key.
"""

import os
import sys
import time
import getpass
from openai import OpenAI

# Output base folder for generated articles
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated-articles")

# Category -> subfolder mapping
CATEGORY_FOLDERS = {
    "How-To Guide": "how-to-guides",
    "Troubleshooting Guide": "troubleshooting",
    "Solution Article": "solutions",
    "Runbook": "runbooks",
}

# Article definitions: (filename, title, category, domain, audience, priority, tags)
ARTICLES = [
    # === 01 - HOW-TO GUIDES ===
    ("HT-003-How-to-Set-Up-Multi-Factor-Authentication.md", "How to Set Up Multi-Factor Authentication", "How-To Guide", "Security", "End-User", "P1-CRITICAL", "mfa, multi-factor, authentication, security, phone, authenticator"),
    ("HT-004-How-to-Access-Shared-Files-in-OneDrive.md", "How to Access Shared Files in OneDrive", "How-To Guide", "OneDrive", "End-User", "P2-HIGH", "onedrive, shared, files, cloud, storage, access"),
    ("HT-005-How-to-Join-a-Teams-Meeting.md", "How to Join a Microsoft Teams Meeting", "How-To Guide", "Collaboration", "End-User", "P1-CRITICAL", "teams, meeting, video, call, conference, join"),
    ("HT-006-How-to-Fix-Outlook-Not-Sending-Emails.md", "How to Fix Outlook Not Sending Emails", "How-To Guide", "Email", "End-User", "P1-CRITICAL", "outlook, email, send, stuck, outbox, not sending"),
    ("HT-009-How-to-Share-Your-Screen-in-Teams.md", "How to Share Your Screen in Teams", "How-To Guide", "Collaboration", "End-User", "P2-HIGH", "teams, screen share, presentation, meeting, display"),
    ("HT-010-How-to-Recover-Deleted-Emails.md", "How to Recover Deleted Emails", "How-To Guide", "Email", "End-User", "P2-HIGH", "email, deleted, recover, trash, outlook, restore"),
    ("HT-011-How-to-Update-Your-Windows-PC.md", "How to Update Your Windows PC", "How-To Guide", "Windows", "End-User", "P2-HIGH", "windows, update, patch, security, restart"),
    ("HT-012-How-to-Set-Up-Out-of-Office-Reply.md", "How to Set Up Out of Office Reply", "How-To Guide", "Email", "End-User", "P2-HIGH", "out of office, auto reply, vacation, email, outlook"),
    ("HT-013-How-to-Access-Shared-Mailbox.md", "How to Access a Shared Mailbox", "How-To Guide", "Email", "End-User", "P2-HIGH", "shared mailbox, email, outlook, team, access"),
    ("HT-014-How-to-Reset-MFA-on-New-Phone.md", "How to Reset MFA on a New Phone", "How-To Guide", "Security", "End-User", "P1-CRITICAL", "mfa, new phone, authenticator, reset, transfer, security"),
    ("HT-015-How-to-Sync-OneDrive-Files-to-PC.md", "How to Sync OneDrive Files to Your PC", "How-To Guide", "OneDrive", "End-User", "P2-HIGH", "onedrive, sync, files, pc, desktop, cloud"),
    ("HT-016-How-to-Change-Email-Signature.md", "How to Change Your Email Signature", "How-To Guide", "Email", "End-User", "P3-LOW", "email, signature, outlook, format, contact"),
    ("HT-017-How-to-Create-Teams-Channel.md", "How to Create a Teams Channel", "How-To Guide", "Collaboration", "End-User", "P3-LOW", "teams, channel, create, group, collaboration"),
    ("HT-018-How-to-Schedule-Teams-Meeting.md", "How to Schedule a Teams Meeting", "How-To Guide", "Collaboration", "End-User", "P2-HIGH", "teams, schedule, meeting, calendar, invite"),
    ("HT-019-How-to-Add-Network-Printer.md", "How to Add a Network Printer", "How-To Guide", "Printing", "End-User", "P2-HIGH", "printer, network, add, install, office"),
    ("HT-020-How-to-Map-Network-Drive.md", "How to Map a Network Drive", "How-To Guide", "Network", "End-User", "P2-HIGH", "network drive, map, shared folder, file server"),
    ("HT-021-How-to-Forward-Email-Automatically.md", "How to Forward Email Automatically", "How-To Guide", "Email", "End-User", "P3-LOW", "email, forward, automatic, redirect, outlook, rules"),
    ("HT-022-How-to-Share-OneDrive-Folder.md", "How to Share a OneDrive Folder", "How-To Guide", "OneDrive", "End-User", "P2-HIGH", "onedrive, share, folder, link, permissions, collaborate"),
    ("HT-023-How-to-Record-Teams-Meeting.md", "How to Record a Teams Meeting", "How-To Guide", "Collaboration", "End-User", "P2-HIGH", "teams, record, meeting, video, save, playback"),
    ("HT-024-How-to-Change-Default-Printer.md", "How to Change Your Default Printer", "How-To Guide", "Printing", "End-User", "P3-LOW", "printer, default, change, settings, windows"),
    ("HT-025-How-to-Create-Email-Distribution-List.md", "How to Create an Email Distribution List", "How-To Guide", "Email", "End-User", "P3-LOW", "email, distribution list, group, contacts, outlook"),
    ("HT-026-How-to-Enable-Teams-Notifications.md", "How to Enable Teams Notifications", "How-To Guide", "Collaboration", "End-User", "P3-LOW", "teams, notifications, alerts, settings, desktop"),
    ("HT-027-How-to-Connect-Bluetooth-Device.md", "How to Connect a Bluetooth Device", "How-To Guide", "Hardware", "End-User", "P2-HIGH", "bluetooth, connect, headset, mouse, keyboard, wireless"),
    ("HT-028-How-to-Change-Display-Settings.md", "How to Change Display Settings", "How-To Guide", "Windows", "End-User", "P3-LOW", "display, resolution, brightness, settings, monitor, screen"),
    ("HT-029-How-to-Clear-Browser-Cache.md", "How to Clear Browser Cache", "How-To Guide", "Browser", "End-User", "P2-HIGH", "browser, cache, clear, chrome, edge, cookies, refresh"),
    ("HT-030-How-to-Save-Email-Attachments.md", "How to Save Email Attachments", "How-To Guide", "Email", "End-User", "P3-LOW", "email, attachments, save, download, outlook, files"),
    ("HT-031-How-to-Use-Teams-Chat.md", "How to Use Teams Chat", "How-To Guide", "Collaboration", "End-User", "P3-LOW", "teams, chat, message, instant, conversation"),
    ("HT-032-How-to-Set-Calendar-Permissions.md", "How to Set Calendar Permissions", "How-To Guide", "Email", "End-User", "P3-LOW", "calendar, permissions, share, outlook, delegate, access"),
    ("HT-033-How-to-Recall-Sent-Email.md", "How to Recall a Sent Email", "How-To Guide", "Email", "End-User", "P2-HIGH", "email, recall, undo, sent, mistake, outlook"),
    ("HT-034-How-to-Connect-External-Monitor.md", "How to Connect an External Monitor", "How-To Guide", "Hardware", "End-User", "P2-HIGH", "monitor, external, display, hdmi, usb-c, dual screen"),
    ("HT-035-How-to-Create-Email-Folders.md", "How to Create Email Folders", "How-To Guide", "Email", "End-User", "P3-LOW", "email, folders, organize, outlook, inbox"),
    ("HT-036-How-to-Enable-Dark-Mode-in-Outlook.md", "How to Enable Dark Mode in Outlook", "How-To Guide", "Email", "End-User", "P3-LOW", "outlook, dark mode, theme, display, settings"),
    ("HT-037-How-to-Set-Email-Priority.md", "How to Set Email Priority", "How-To Guide", "Email", "End-User", "P3-LOW", "email, priority, high, importance, outlook, flag"),
    ("HT-038-How-to-Create-Quick-Steps-in-Outlook.md", "How to Create Quick Steps in Outlook", "How-To Guide", "Email", "End-User", "P3-LOW", "outlook, quick steps, automation, rules, shortcut"),
    ("HT-039-How-to-Export-Contacts.md", "How to Export Contacts", "How-To Guide", "Email", "End-User", "P3-LOW", "contacts, export, outlook, csv, backup"),
    ("HT-040-How-to-Set-Custom-Teams-Status.md", "How to Set a Custom Teams Status", "How-To Guide", "Collaboration", "End-User", "P3-LOW", "teams, status, custom, message, availability"),
    ("HT-041-How-to-Pin-Teams-Conversation.md", "How to Pin a Teams Conversation", "How-To Guide", "Collaboration", "End-User", "P3-LOW", "teams, pin, conversation, chat, favorite"),
    ("HT-042-How-to-Use-OneDrive-Personal-Vault.md", "How to Use OneDrive Personal Vault", "How-To Guide", "OneDrive", "End-User", "P3-LOW", "onedrive, personal vault, secure, files, sensitive"),
    ("HT-043-How-to-Create-Outlook-Category.md", "How to Create Outlook Categories", "How-To Guide", "Email", "End-User", "P3-LOW", "outlook, categories, color, organize, label"),
    ("HT-044-How-to-Schedule-Email-Delivery.md", "How to Schedule Email Delivery", "How-To Guide", "Email", "End-User", "P3-LOW", "email, schedule, delay, send later, outlook"),
    ("HT-045-How-to-Set-Focused-Inbox.md", "How to Set Up Focused Inbox", "How-To Guide", "Email", "End-User", "P3-LOW", "outlook, focused inbox, filter, priority, email"),
    ("HT-046-How-to-Create-Email-Template.md", "How to Create an Email Template", "How-To Guide", "Email", "End-User", "P3-LOW", "email, template, outlook, reuse, quick parts"),
    ("HT-047-How-to-Set-Teams-Background.md", "How to Set a Teams Background", "How-To Guide", "Collaboration", "End-User", "P3-LOW", "teams, background, virtual, blur, video, meeting"),
    ("HT-048-How-to-Archive-Old-Emails.md", "How to Archive Old Emails", "How-To Guide", "Email", "End-User", "P3-LOW", "email, archive, old, storage, outlook, cleanup"),
    ("HT-049-How-to-Create-Desktop-Shortcut.md", "How to Create a Desktop Shortcut", "How-To Guide", "Windows", "End-User", "P3-LOW", "desktop, shortcut, icon, quick access, windows"),
    ("HT-050-How-to-Check-Windows-Version.md", "How to Check Your Windows Version", "How-To Guide", "Windows", "End-User", "P3-LOW", "windows, version, check, system, about, update"),

    # === 02 - TROUBLESHOOTING GUIDES ===
    ("TS-001-Network-Connectivity-Troubleshooting.md", "Troubleshoot Network Connectivity Issues", "Troubleshooting Guide", "Network", "End-User", "P1-CRITICAL", "network, connectivity, internet, no connection, wifi, ethernet"),
    ("TS-002-Email-Sync-Issues-Diagnostic.md", "Troubleshoot Email Sync Issues", "Troubleshooting Guide", "Email", "End-User", "P1-CRITICAL", "email, sync, not updating, outlook, refresh, delay"),
    ("TS-003-Teams-Audio-Video-Troubleshooting.md", "Troubleshoot Teams Audio and Video Issues", "Troubleshooting Guide", "Collaboration", "End-User", "P1-CRITICAL", "teams, audio, video, microphone, camera, sound"),
    ("TS-004-Account-Lockout-Diagnostic.md", "Troubleshoot Account Lockout Issues", "Troubleshooting Guide", "Security", "End-User", "P1-CRITICAL", "account, locked, lockout, password, access denied"),
    ("TS-005-Slow-Computer-Performance-Diagnostic.md", "Troubleshoot Slow Computer Performance", "Troubleshooting Guide", "Windows", "End-User", "P1-CRITICAL", "slow, computer, performance, lag, freeze, speed"),
    ("TS-006-Printer-Not-Working-Troubleshooting.md", "Troubleshoot Printer Not Working", "Troubleshooting Guide", "Printing", "End-User", "P2-HIGH", "printer, not working, offline, error, print, jam"),
    ("TS-007-OneDrive-Sync-Issues-Diagnostic.md", "Troubleshoot OneDrive Sync Issues", "Troubleshooting Guide", "OneDrive", "End-User", "P2-HIGH", "onedrive, sync, not syncing, error, conflict, cloud"),
    ("TS-008-WiFi-Connection-Problems-Diagnostic.md", "Troubleshoot WiFi Connection Problems", "Troubleshooting Guide", "Network", "End-User", "P1-CRITICAL", "wifi, wireless, connection, dropping, slow, signal"),
    ("TS-009-Outlook-Wont-Open-Troubleshooting.md", "Troubleshoot Outlook Won't Open", "Troubleshooting Guide", "Email", "End-User", "P1-CRITICAL", "outlook, wont open, crash, not responding, stuck, loading"),
    ("TS-010-MFA-Not-Working-Diagnostic.md", "Troubleshoot MFA Not Working", "Troubleshooting Guide", "Security", "End-User", "P1-CRITICAL", "mfa, not working, authenticator, code, push, verification"),
    ("TS-011-Email-Delivery-Issues-Diagnostic.md", "Troubleshoot Email Delivery Issues", "Troubleshooting Guide", "Email", "End-User", "P2-HIGH", "email, not delivered, bounce, rejected, spam, missing"),
    ("TS-012-File-Access-Denied-Troubleshooting.md", "Troubleshoot File Access Denied Errors", "Troubleshooting Guide", "Windows", "End-User", "P2-HIGH", "file, access denied, permissions, cannot open, restricted"),
    ("TS-013-Teams-Notification-Issues-Diagnostic.md", "Troubleshoot Teams Notification Issues", "Troubleshooting Guide", "Collaboration", "End-User", "P3-LOW", "teams, notifications, not receiving, alerts, settings"),
    ("TS-014-Printer-Queue-Stuck-Troubleshooting.md", "Troubleshoot Printer Queue Stuck", "Troubleshooting Guide", "Printing", "End-User", "P2-HIGH", "printer, queue, stuck, pending, cancel, spooler"),
    ("TS-015-External-Monitor-Not-Working-Diagnostic.md", "Troubleshoot External Monitor Not Working", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "monitor, external, not working, no display, detect, hdmi"),
    ("TS-016-Shared-Mailbox-Access-Issues.md", "Troubleshoot Shared Mailbox Access Issues", "Troubleshooting Guide", "Email", "End-User", "P2-HIGH", "shared mailbox, access, permissions, outlook, error"),
    ("TS-017-Calendar-Sync-Problems-Diagnostic.md", "Troubleshoot Calendar Sync Problems", "Troubleshooting Guide", "Email", "End-User", "P2-HIGH", "calendar, sync, not updating, outlook, meetings, events"),
    ("TS-018-Teams-Screen-Share-Not-Working.md", "Troubleshoot Teams Screen Share Not Working", "Troubleshooting Guide", "Collaboration", "End-User", "P2-HIGH", "teams, screen share, not working, black, permissions"),
    ("TS-019-OneDrive-Storage-Full-Diagnostic.md", "Troubleshoot OneDrive Storage Full", "Troubleshooting Guide", "OneDrive", "End-User", "P2-HIGH", "onedrive, storage, full, space, quota, cleanup"),
    ("TS-020-Keyboard-Not-Working-Troubleshooting.md", "Troubleshoot Keyboard Not Working", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "keyboard, not working, keys, typing, input, stuck"),
    ("TS-021-Mouse-Issues-Diagnostic.md", "Troubleshoot Mouse Issues", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "mouse, not working, cursor, clicking, wireless, tracking"),
    ("TS-022-Bluetooth-Connection-Problems.md", "Troubleshoot Bluetooth Connection Problems", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "bluetooth, connection, pairing, disconnecting, device"),
    ("TS-023-Microphone-Not-Detected-Diagnostic.md", "Troubleshoot Microphone Not Detected", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "microphone, not detected, audio, input, teams, recording"),
    ("TS-024-Webcam-Issues-Troubleshooting.md", "Troubleshoot Webcam Issues", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "webcam, camera, not working, video, teams, blurry"),
    ("TS-025-USB-Device-Not-Recognized.md", "Troubleshoot USB Device Not Recognized", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "usb, device, not recognized, drive, flash, port"),
    ("TS-026-Sound-Not-Working-Diagnostic.md", "Troubleshoot Sound Not Working", "Troubleshooting Guide", "Hardware", "End-User", "P2-HIGH", "sound, audio, not working, speakers, headphones, volume"),
    ("TS-027-Email-Signature-Not-Showing.md", "Troubleshoot Email Signature Not Showing", "Troubleshooting Guide", "Email", "End-User", "P3-LOW", "email, signature, not showing, missing, outlook"),
    ("TS-028-Teams-Background-Not-Working.md", "Troubleshoot Teams Background Not Working", "Troubleshooting Guide", "Collaboration", "End-User", "P3-LOW", "teams, background, not working, blur, virtual"),
    ("TS-029-OneDrive-Files-Not-Opening.md", "Troubleshoot OneDrive Files Not Opening", "Troubleshooting Guide", "OneDrive", "End-User", "P2-HIGH", "onedrive, files, not opening, error, sync, access"),
    ("TS-030-Search-Not-Working-in-Outlook.md", "Troubleshoot Search Not Working in Outlook", "Troubleshooting Guide", "Email", "End-User", "P2-HIGH", "outlook, search, not working, find, index, results"),

    # === 03 - SOLUTION ARTICLES ===
    ("SOL-001-Fix-DNS-Configuration-Issues.md", "Fix DNS Configuration Issues", "Solution Article", "Network", "IT-Support", "P2-HIGH", "dns, configuration, resolve, internet, nameserver"),
    ("SOL-002-Clear-Teams-Cache.md", "Clear Microsoft Teams Cache", "Solution Article", "Collaboration", "End-User", "P2-HIGH", "teams, cache, clear, performance, fix, reset"),
    ("SOL-003-Rebuild-Outlook-Profile.md", "Rebuild Outlook Profile", "Solution Article", "Email", "IT-Support", "P2-HIGH", "outlook, profile, rebuild, repair, corrupt, new"),
    ("SOL-004-Fix-Outlook-Stuck-on-Loading-Profile.md", "Fix Outlook Stuck on Loading Profile", "Solution Article", "Email", "End-User", "P1-CRITICAL", "outlook, stuck, loading, profile, hang, startup"),
    ("SOL-005-Repair-OneDrive-Sync.md", "Repair OneDrive Sync", "Solution Article", "OneDrive", "End-User", "P2-HIGH", "onedrive, sync, repair, reset, fix, link"),
    ("SOL-006-Reset-Network-Adapter.md", "Reset Network Adapter", "Solution Article", "Network", "End-User", "P2-HIGH", "network, adapter, reset, connectivity, ip, flush"),
    ("SOL-007-Fix-Account-Lockout.md", "Fix Account Lockout", "Solution Article", "Security", "IT-Support", "P1-CRITICAL", "account, lockout, unlock, password, active directory"),
    ("SOL-008-Restart-Print-Spooler-Service.md", "Restart Print Spooler Service", "Solution Article", "Printing", "End-User", "P2-HIGH", "print, spooler, restart, service, stuck, queue"),
    ("SOL-009-Fix-Teams-Audio-Device-Settings.md", "Fix Teams Audio Device Settings", "Solution Article", "Collaboration", "End-User", "P2-HIGH", "teams, audio, device, settings, microphone, speaker"),
    ("SOL-010-Clear-Credential-Manager.md", "Clear Windows Credential Manager", "Solution Article", "Security", "IT-Support", "P2-HIGH", "credential, manager, clear, password, cached, stored"),
    ("SOL-011-Reset-WiFi-Settings.md", "Reset WiFi Settings", "Solution Article", "Network", "End-User", "P2-HIGH", "wifi, reset, settings, forget, network, reconnect"),
    ("SOL-012-Fix-Outlook-Search-Not-Working.md", "Fix Outlook Search Not Working", "Solution Article", "Email", "End-User", "P2-HIGH", "outlook, search, not working, index, rebuild, repair"),
    ("SOL-013-Repair-Office-Installation.md", "Repair Microsoft Office Installation", "Solution Article", "Windows", "End-User", "P2-HIGH", "office, repair, install, fix, corrupt, microsoft 365"),
    ("SOL-014-Fix-MFA-Authentication-Loop.md", "Fix MFA Authentication Loop", "Solution Article", "Security", "IT-Support", "P1-CRITICAL", "mfa, loop, authentication, stuck, repeating, verify"),
    ("SOL-015-Clear-Windows-Update-Cache.md", "Clear Windows Update Cache", "Solution Article", "Windows", "End-User", "P2-HIGH", "windows, update, cache, clear, stuck, failed"),
    ("SOL-016-Fix-Printer-Offline-Status.md", "Fix Printer Offline Status", "Solution Article", "Printing", "End-User", "P2-HIGH", "printer, offline, status, online, fix, connection"),
    ("SOL-017-Resolve-IP-Address-Conflict.md", "Resolve IP Address Conflict", "Solution Article", "Network", "IT-Support", "P2-HIGH", "ip, address, conflict, network, duplicate, dhcp"),
    ("SOL-018-Fix-OneDrive-Red-X-Error.md", "Fix OneDrive Red X Error", "Solution Article", "OneDrive", "End-User", "P2-HIGH", "onedrive, red x, error, sync, not syncing, icon"),
    ("SOL-019-Reset-Teams-Settings.md", "Reset Microsoft Teams Settings", "Solution Article", "Collaboration", "End-User", "P2-HIGH", "teams, reset, settings, default, fix, reinstall"),
    ("SOL-020-Fix-Calendar-Permission-Issues.md", "Fix Calendar Permission Issues", "Solution Article", "Email", "End-User", "P2-HIGH", "calendar, permissions, sharing, access, delegate, outlook"),
    ("SOL-021-Repair-Corrupted-OST-File.md", "Repair Corrupted OST File", "Solution Article", "Email", "IT-Support", "P2-HIGH", "ost, file, corrupted, repair, outlook, data"),
    ("SOL-022-Fix-Display-Scaling-Issues.md", "Fix Display Scaling Issues", "Solution Article", "Windows", "End-User", "P3-LOW", "display, scaling, blurry, dpi, resolution, text"),
    ("SOL-023-Reset-Edge-Browser-Settings.md", "Reset Microsoft Edge Browser Settings", "Solution Article", "Browser", "End-User", "P3-LOW", "edge, browser, reset, settings, default, fix"),
    ("SOL-024-Fix-Bluetooth-Pairing-Problems.md", "Fix Bluetooth Pairing Problems", "Solution Article", "Hardware", "End-User", "P2-HIGH", "bluetooth, pairing, failed, connect, device, remove"),
    ("SOL-025-Resolve-Duplicate-Email-Issue.md", "Resolve Duplicate Email Issue", "Solution Article", "Email", "End-User", "P3-LOW", "email, duplicate, copies, outlook, sync, multiple"),
    ("SOL-026-Fix-Shared-Drive-Mapping.md", "Fix Shared Drive Mapping", "Solution Article", "Network", "End-User", "P2-HIGH", "shared drive, mapping, network, disconnected, red x"),
    ("SOL-027-Reset-Windows-Audio-Service.md", "Reset Windows Audio Service", "Solution Article", "Hardware", "End-User", "P2-HIGH", "audio, service, reset, sound, not working, windows"),
    ("SOL-028-Fix-File-Explorer-Not-Responding.md", "Fix File Explorer Not Responding", "Solution Article", "Windows", "End-User", "P2-HIGH", "file explorer, not responding, crash, hang, frozen"),
    ("SOL-029-Resolve-OneDrive-Sync-Conflicts.md", "Resolve OneDrive Sync Conflicts", "Solution Article", "OneDrive", "End-User", "P2-HIGH", "onedrive, sync, conflict, duplicate, version, resolve"),
    ("SOL-030-Fix-Teams-Cant-Sign-In.md", "Fix Teams Can't Sign In", "Solution Article", "Collaboration", "End-User", "P1-CRITICAL", "teams, sign in, login, error, cant, authentication"),
    ("SOL-031-Reset-Windows-Search-Index.md", "Reset Windows Search Index", "Solution Article", "Windows", "End-User", "P3-LOW", "windows, search, index, rebuild, not working, results"),
    ("SOL-032-Fix-Email-Stuck-in-Outbox.md", "Fix Email Stuck in Outbox", "Solution Article", "Email", "End-User", "P2-HIGH", "email, stuck, outbox, not sending, outlook, queued"),
    ("SOL-033-Repair-Network-Location-Services.md", "Repair Network Location Services", "Solution Article", "Network", "IT-Support", "P3-LOW", "network, location, services, private, public, firewall"),
    ("SOL-034-Fix-Taskbar-Not-Hiding.md", "Fix Taskbar Not Hiding", "Solution Article", "Windows", "End-User", "P3-LOW", "taskbar, not hiding, auto hide, fullscreen, windows"),
    ("SOL-035-Reset-Start-Menu.md", "Reset Start Menu", "Solution Article", "Windows", "End-User", "P3-LOW", "start menu, reset, not working, tiles, search, windows"),
    ("SOL-036-Fix-Notification-Center-Issues.md", "Fix Notification Center Issues", "Solution Article", "Windows", "End-User", "P3-LOW", "notification, center, not showing, alerts, windows, action"),
    ("SOL-037-Repair-Windows-Defender.md", "Repair Windows Defender", "Solution Article", "Security", "IT-Support", "P2-HIGH", "windows defender, antivirus, repair, not working, scan"),
    ("SOL-038-Fix-Time-Date-Sync-Issues.md", "Fix Time and Date Sync Issues", "Solution Article", "Windows", "End-User", "P2-HIGH", "time, date, sync, wrong, clock, timezone, ntp"),
    ("SOL-039-Reset-Microsoft-Store.md", "Reset Microsoft Store", "Solution Article", "Windows", "End-User", "P3-LOW", "microsoft store, reset, not working, cache, apps, download"),
    ("SOL-040-Fix-Screenshot-Tool-Not-Working.md", "Fix Screenshot Tool Not Working", "Solution Article", "Windows", "End-User", "P3-LOW", "screenshot, snipping tool, not working, print screen, capture"),
    ("SOL-041-Resolve-Font-Display-Issues.md", "Resolve Font Display Issues", "Solution Article", "Windows", "End-User", "P3-LOW", "font, display, blurry, missing, cleartype, rendering"),
    ("SOL-042-Fix-Clipboard-Not-Working.md", "Fix Clipboard Not Working", "Solution Article", "Windows", "End-User", "P3-LOW", "clipboard, copy, paste, not working, history, clear"),
    ("SOL-043-Reset-Windows-Color-Profile.md", "Reset Windows Color Profile", "Solution Article", "Windows", "End-User", "P3-LOW", "color, profile, display, calibration, reset, settings"),
    ("SOL-044-Fix-Sticky-Keys-Issues.md", "Fix Sticky Keys Issues", "Solution Article", "Windows", "End-User", "P3-LOW", "sticky keys, accessibility, keyboard, modifier, disable"),
    ("SOL-045-Repair-Corrupted-User-Profile.md", "Repair Corrupted User Profile", "Solution Article", "Windows", "IT-Support", "P1-CRITICAL", "user profile, corrupted, repair, login, temporary, fix"),

    # === 04 - RUNBOOKS (IT Admin) ===
    ("RB-001-Provision-New-User-Account.md", "Provision New User Account", "Runbook", "Administration", "IT-Support", "P1-CRITICAL", "provision, new user, account, create, onboarding, active directory"),
    ("RB-002-Reset-User-Password-Admin.md", "Reset User Password (Admin)", "Runbook", "Administration", "IT-Support", "P1-CRITICAL", "password, reset, admin, user, active directory, unlock"),
    ("RB-003-Reset-User-MFA-Device.md", "Reset User MFA Device", "Runbook", "Security", "IT-Support", "P1-CRITICAL", "mfa, reset, device, authenticator, user, entra"),
    ("RB-004-Grant-Shared-Mailbox-Access.md", "Grant Shared Mailbox Access", "Runbook", "Email", "IT-Support", "P2-HIGH", "shared mailbox, access, grant, permissions, exchange"),
    ("RB-005-Add-User-to-Distribution-List.md", "Add User to Distribution List", "Runbook", "Email", "IT-Support", "P3-LOW", "distribution list, add, user, group, exchange"),
    ("RB-006-Check-User-License-Status.md", "Check User License Status", "Runbook", "Administration", "IT-Support", "P2-HIGH", "license, status, check, microsoft 365, assigned, user"),
    ("RB-007-Unlock-User-Account.md", "Unlock User Account", "Runbook", "Administration", "IT-Support", "P1-CRITICAL", "unlock, account, locked, user, active directory"),
    ("RB-008-Retrieve-WiFi-Password.md", "Retrieve WiFi Password", "Runbook", "Network", "IT-Support", "P3-LOW", "wifi, password, retrieve, network, ssid, key"),
    ("RB-009-Deactivate-User-Account.md", "Deactivate User Account", "Runbook", "Administration", "IT-Support", "P1-CRITICAL", "deactivate, disable, user, account, offboarding, terminate"),
    ("RB-010-Assign-Microsoft-365-License.md", "Assign Microsoft 365 License", "Runbook", "Administration", "IT-Support", "P2-HIGH", "license, assign, microsoft 365, user, entra, admin"),
    ("RB-011-Create-Distribution-List.md", "Create Distribution List", "Runbook", "Email", "IT-Support", "P3-LOW", "distribution list, create, email, group, exchange"),
    ("RB-012-Move-User-to-Different-OU.md", "Move User to Different OU", "Runbook", "Administration", "IT-Support", "P3-LOW", "ou, organizational unit, move, user, active directory"),
    ("RB-013-Check-Ticket-Status.md", "Check Ticket Status", "Runbook", "Administration", "IT-Support", "P3-LOW", "ticket, status, check, helpdesk, support, open"),
    ("RB-014-Retrieve-Asset-Information.md", "Retrieve Asset Information", "Runbook", "Administration", "IT-Support", "P3-LOW", "asset, information, retrieve, computer, serial, inventory"),
    ("RB-015-Check-Service-Status.md", "Check Service Status", "Runbook", "Administration", "IT-Support", "P2-HIGH", "service, status, check, outage, microsoft 365, health"),
    ("RB-016-Configure-Email-Forwarding.md", "Configure Email Forwarding", "Runbook", "Email", "IT-Support", "P2-HIGH", "email, forwarding, configure, redirect, exchange, admin"),
    ("RB-017-Set-Mailbox-Size-Limit.md", "Set Mailbox Size Limit", "Runbook", "Email", "IT-Support", "P3-LOW", "mailbox, size, limit, quota, exchange, storage"),
    ("RB-018-Enable-Litigation-Hold.md", "Enable Litigation Hold", "Runbook", "Email", "IT-Support", "P2-HIGH", "litigation, hold, legal, compliance, mailbox, preserve"),
    ("RB-019-Export-User-Mailbox.md", "Export User Mailbox", "Runbook", "Email", "IT-Support", "P2-HIGH", "export, mailbox, pst, user, backup, exchange"),
    ("RB-020-Create-Shared-Mailbox.md", "Create Shared Mailbox", "Runbook", "Email", "IT-Support", "P2-HIGH", "shared mailbox, create, exchange, team, email"),
    ("RB-021-Configure-Mobile-Device-Policy.md", "Configure Mobile Device Policy", "Runbook", "Security", "IT-Support", "P2-HIGH", "mobile, device, policy, mdm, intune, compliance"),
    ("RB-022-Run-Compliance-Report.md", "Run Compliance Report", "Runbook", "Security", "IT-Support", "P2-HIGH", "compliance, report, audit, security, microsoft 365"),
    ("RB-023-Configure-Email-Retention-Policy.md", "Configure Email Retention Policy", "Runbook", "Email", "IT-Support", "P2-HIGH", "retention, policy, email, archive, compliance, exchange"),
    ("RB-024-Set-Up-Room-Mailbox.md", "Set Up Room Mailbox", "Runbook", "Email", "IT-Support", "P3-LOW", "room, mailbox, calendar, conference, booking, resource"),
    ("RB-025-Configure-External-Sharing-Settings.md", "Configure External Sharing Settings", "Runbook", "Security", "IT-Support", "P2-HIGH", "external, sharing, settings, onedrive, sharepoint, guest"),
]

# GPT prompt template for generating articles
ARTICLE_PROMPT = """Write a detailed IT support knowledge base article with the following requirements:

Title: {title}
Category: {category}
Domain: {domain}
Audience: {audience}

Format the article EXACTLY like this (in markdown):

---
id: {article_id}
title: {title}
category: {category}
audience: {audience}
domain: {domain}
tags: {tags}
priority: {priority}
related_articles: []
last_updated: 2024-12-11
---

# {title}

## When to Use This Article
[1-2 sentences explaining when this article applies]

## Prerequisites
- [List 2-4 prerequisites]

## Step-by-Step Instructions

### Step 1: [Action Title]
[Detailed instructions with specific clicks, menus, and settings]

### Step 2: [Action Title]
[Continue with specific, actionable steps]

[Add as many steps as needed - typically 3-6 steps]

## Common Issues

### Issue 1: [Problem Name]
**Symptoms:** [What the user sees]
**Solution:** [Specific fix]

### Issue 2: [Problem Name]
**Symptoms:** [What the user sees]
**Solution:** [Specific fix]

## Escalation Triggers
- [When to escalate - list 2-4 triggers]

## Success Criteria
- [How to verify it's working - list 2-3 criteria]

## Related Articles
- [List 2-3 related article references]

IMPORTANT RULES:
- Write REAL, SPECIFIC instructions (not placeholders)
- Include actual menu paths, button names, and keyboard shortcuts
- For Windows instructions, reference Windows 10/11
- For IT admin runbooks, include PowerShell commands where appropriate
- Keep it practical and actionable
- Target the specified audience ({audience})
"""


def main():
    print("\n=== TactivAI KB Article Generator ===\n")
    print(f"This will generate {len(ARTICLES)} articles with real content using OpenAI GPT.\n")
    print("Output structure:")
    for cat, folder in CATEGORY_FOLDERS.items():
        count = sum(1 for _, _, c, *_ in ARTICLES if c == cat)
        print(f"  {folder}/ ({count} articles)")
    print()

    # Get API key
    api_key = input("OpenAI API Key: ").strip()

    try:
        client = OpenAI(api_key=api_key)
        # Quick validation
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("OpenAI connection validated.\n")
    except Exception as e:
        print(f"OpenAI connection failed: {e}")
        sys.exit(1)

    # Create output directories for each category
    for folder in CATEGORY_FOLDERS.values():
        os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

    # Check which articles already exist (across all subfolders)
    existing = set()
    for folder in CATEGORY_FOLDERS.values():
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
            existing.update(os.listdir(folder_path))

    remaining = [(f, t, c, d, a, p, tags) for f, t, c, d, a, p, tags in ARTICLES if f not in existing]

    if existing:
        print(f"Found {len(existing)} already generated. Skipping those.")
    print(f"Generating {len(remaining)} articles...\n")

    if not remaining:
        print("All articles already generated!")
        sys.exit(0)

    success = 0
    failed = 0

    for i, (filename, title, category, domain, audience, priority, tags) in enumerate(remaining, 1):
        article_id = filename.split("-")[0] + "-" + filename.split("-")[1]
        subfolder = CATEGORY_FOLDERS.get(category, "other")
        print(f"[{i}/{len(remaining)}] [{subfolder}] {filename}...", end=" ", flush=True)

        prompt = ARTICLE_PROMPT.format(
            title=title,
            category=category,
            domain=domain,
            audience=audience,
            priority=priority,
            tags=tags,
            article_id=article_id
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a technical writer creating IT support knowledge base articles. Write clear, specific, actionable instructions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            content = response.choices[0].message.content

            filepath = os.path.join(BASE_DIR, subfolder, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            success += 1
            print("OK")

            # Brief pause to respect rate limits
            time.sleep(0.5)

        except Exception as e:
            failed += 1
            print(f"FAILED ({e})")
            time.sleep(1)

    print(f"\n=== Generation Complete ===")
    print(f"  Generated: {success}")
    print(f"  Failed:    {failed}")
    print(f"  Skipped:   {len(existing)}")
    print(f"  Output:    {BASE_DIR}")
    for cat, folder in CATEGORY_FOLDERS.items():
        folder_path = os.path.join(BASE_DIR, folder)
        count = len(os.listdir(folder_path)) if os.path.isdir(folder_path) else 0
        print(f"    {folder}/ - {count} articles")
    print(f"\nNext: Use upload_app.py to upload each folder separately to Supabase.")
    print(f"Set the 'Category tag' to match each folder (e.g., 'how-to-guides', 'troubleshooting', etc.)")


if __name__ == "__main__":
    main()
