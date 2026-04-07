-- ============================================================
-- Isaac Email Fetcher
-- Fetches emails from the last 24 hours from Microsoft Outlook
-- and saves them as a markdown file
-- ============================================================

-- Configuration
set hoursBack to 24
set outputFolder to (POSIX path of (path to home folder)) & "isaac-email-fetcher/output/"
set dateStamp to do shell script "date '+%Y-%m-%d_%H-%M'"
set outputFile to outputFolder & "emails_" & dateStamp & ".md"

-- Calculate cutoff time (24 hours ago)
set cutoffTime to (current date) - (hoursBack * hours)

-- Start markdown content
set mdContent to "# 📬 Isaac Email Report" & return
set mdContent to mdContent & "**Generated:** " & (current date as string) & return
set mdContent to mdContent & "**Period:** Last " & hoursBack & " hours" & return
set mdContent to mdContent & return & "---" & return & return

set emailCount to 0

tell application "Microsoft Outlook"
	-- Loop through all inbox messages
	set inboxMessages to messages of inbox

	repeat with msg in inboxMessages
		set msgTime to time received of msg

		-- Only include emails from the last 24 hours
		if msgTime >= cutoffTime then
			set emailCount to emailCount + 1

			-- Get email details
			set msgSubject to subject of msg
			set msgSender to ""
			set msgBody to ""
			set msgDate to msgTime as string

			-- Get sender name and email
			try
				set senderRecord to sender of msg
				set senderName to display name of senderRecord
				set senderEmail to address of senderRecord
				set msgSender to senderName & " <" & senderEmail & ">"
			on error
				set msgSender to "Unknown Sender"
			end try

			-- Get plain text body (truncated to 500 chars to keep file clean)
			try
				set msgBody to plain text content of msg
				if length of msgBody > 500 then
					set msgBody to (text 1 thru 500 of msgBody) & "..."
				end if
			on error
				set msgBody to "[No body content]"
			end try

			-- Check if email is read
			set readStatus to ""
			if is read of msg is false then
				set readStatus to " 🔵"
			end if

			-- Append to markdown
			set mdContent to mdContent & "## " & emailCount & ". " & msgSubject & readStatus & return
			set mdContent to mdContent & "**From:** " & msgSender & return
			set mdContent to mdContent & "**Received:** " & msgDate & return
			set mdContent to mdContent & return
			set mdContent to mdContent & "> " & msgBody & return
			set mdContent to mdContent & return & "---" & return & return
		end if
	end repeat
end tell

-- Add summary at top
set summary to "**Total emails found:** " & emailCount & return & return
set mdContent to (text 1 thru (offset of "---" in mdContent) - 1 of mdContent) & summary & (text (offset of "---" in mdContent) thru -1 of mdContent)

-- Write to file
do shell script "mkdir -p " & quoted form of outputFolder
do shell script "cat > " & quoted form of outputFile & " << 'ISAACEOF'" & return & mdContent & return & "ISAACEOF"

-- Confirm
display notification "Saved " & emailCount & " emails to output folder" with title "Isaac ✅"

return outputFile
