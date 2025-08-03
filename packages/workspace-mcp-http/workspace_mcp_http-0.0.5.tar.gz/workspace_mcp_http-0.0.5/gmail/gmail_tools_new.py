"""
Google Gmail MCP Tools - Updated for Access Token Authentication

This module provides MCP tools for interacting with the Gmail API using access token auth.
"""

import logging
import asyncio
import base64
from typing import Optional, List, Dict, Literal
from email.mime.text import MIMEText

from auth.token_auth import get_authenticated_google_service, GoogleAuthenticationError
from core.session_server import register_tool_with_transport
from core.utils import handle_http_errors

logger = logging.getLogger(__name__)

# Required scopes for Gmail operations
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels"
]

def _extract_message_body(payload):
    """
    Helper function to extract plain text body from a Gmail message payload.
    """
    body_data = ""
    parts = [payload] if "parts" not in payload else payload.get("parts", [])

    part_queue = list(parts)
    while part_queue:
        part = part_queue.pop(0)
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            data = base64.urlsafe_b64decode(part["body"]["data"])
            body_data = data.decode("utf-8", errors="ignore")
            break
        elif part.get("mimeType", "").startswith("multipart/") and "parts" in part:
            part_queue.extend(part.get("parts", []))

    if (
        not body_data
        and payload.get("mimeType") == "text/plain"
        and payload.get("body", {}).get("data")
    ):
        data = base64.urlsafe_b64decode(payload["body"]["data"])
        body_data = data.decode("utf-8", errors="ignore")

    return body_data

def _extract_headers(payload: dict, header_names: List[str]) -> Dict[str, str]:
    """Extract specified headers from a Gmail message payload."""
    headers = {}
    for header in payload.get("headers", []):
        if header["name"] in header_names:
            headers[header["name"]] = header["value"]
    return headers

def _generate_gmail_web_url(item_id: str, account_index: int = 0) -> str:
    """Generate Gmail web interface URL for a message or thread ID."""
    return f"https://mail.google.com/mail/u/{account_index}/#all/{item_id}"

def _format_gmail_results_plain(messages: list, query: str) -> str:
    """Format Gmail search results in clean, LLM-friendly plain text."""
    if not messages:
        return f"No messages found for query: '{query}'"

    lines = [
        f"Found {len(messages)} messages matching '{query}':",
        "",
        "📧 MESSAGES:",
    ]

    for i, msg in enumerate(messages, 1):
        message_url = _generate_gmail_web_url(msg["id"])
        thread_url = _generate_gmail_web_url(msg["threadId"])

        lines.extend(
            [
                f"  {i}. Message ID: {msg['id']}",
                f"     Web Link: {message_url}",
                f"     Thread ID: {msg['threadId']}",
                f"     Thread Link: {thread_url}",
                "",
            ]
        )

    lines.extend(
        [
            "💡 USAGE:",
            "  • Pass the Message IDs **as a list** to get_gmail_messages_content_batch()",
            "    e.g. get_gmail_messages_content_batch(message_ids=[...])",
            "  • Pass the Thread IDs to get_gmail_thread_content() (single) or get_gmail_threads_content_batch() (batch)",
        ]
    )

    return "\n".join(lines)

@handle_http_errors("search_gmail_messages", is_read_only=True)
async def search_gmail_messages(
    query: str,
    max_results: int = 10,
    include_body: bool = True
) -> str:
    """
    Search Gmail messages using Gmail search syntax.
    
    Args:
        query: Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting')
        max_results: Maximum number of messages to return (default: 10)
        include_body: Whether to include message body content (default: True)
    
    Returns:
        Formatted search results with full email content
    """
    try:
        # Get authenticated Gmail service
        service = await get_authenticated_google_service("gmail", "v1", "search_gmail_messages")
        
        logger.info(f"[search_gmail_messages] Query: '{query}', Include body: {include_body}")

        # Search for messages
        response = await asyncio.to_thread(
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute
        )
        
        messages = response.get("messages", [])
        if not messages:
            return f"No messages found for query: '{query}'"

        if not include_body:
            # Use the original formatting for backward compatibility
            formatted_output = _format_gmail_results_plain(messages, query)
            logger.info(f"[search_gmail_messages] Found {len(messages)} messages")
            return formatted_output

        # Get detailed information for each message with full content
        result_lines = [f"Found {len(messages)} messages matching '{query}':", ""]
        
        for i, message in enumerate(messages, 1):
            msg_detail = await asyncio.to_thread(
                service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute
            )
            
            # Extract headers
            headers = _extract_headers(
                msg_detail['payload'], 
                ['From', 'To', 'Subject', 'Date']
            )
            
            # Extract body content
            body_content = _extract_message_body(msg_detail['payload'])
            
            # Add message details to result
            result_lines.extend([
                f"=== Message {i} ===",
                f"Message ID: {message['id']}",
                f"Subject: {headers.get('Subject', 'No Subject')}",
                f"From: {headers.get('From', 'Unknown')}",
                f"To: {headers.get('To', 'Unknown')}",
                f"Date: {headers.get('Date', 'Unknown')}",
                f"Web Link: {_generate_gmail_web_url(message['id'])}",
                "",
                "--- EMAIL CONTENT ---",
                body_content or "[No text/plain body found]",
                "",
            ])

        logger.info(f"[search_gmail_messages] Found {len(messages)} messages with content")
        return "\n".join(result_lines)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error searching Gmail messages: {e}")
        return f"Error searching Gmail messages: {str(e)}"

@handle_http_errors("get_gmail_message_content", is_read_only=True)
async def get_gmail_message_content(message_id: str) -> str:
    """
    Get detailed information about a specific Gmail message.
    
    Args:
        message_id: The Gmail message ID
    
    Returns:
        Detailed message information
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_message_content")
        
        logger.info(f"[get_gmail_message_content] Invoked. Message ID: '{message_id}'")

        # Fetch message metadata first to get headers
        message_metadata = await asyncio.to_thread(
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Subject", "From"],
            )
            .execute
        )

        headers = {
            h["name"]: h["value"]
            for h in message_metadata.get("payload", {}).get("headers", [])
        }
        subject = headers.get("Subject", "(no subject)")
        sender = headers.get("From", "(unknown sender)")

        # Now fetch the full message to get the body parts
        message_full = await asyncio.to_thread(
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",  # Request full payload for body
            )
            .execute
        )

        # Extract the plain text body using helper function
        payload = message_full.get("payload", {})
        body_data = _extract_message_body(payload)

        content_text = "\n".join(
            [
                f"Subject: {subject}",
                f"From:    {sender}",
                f"\n--- BODY ---\n{body_data or '[No text/plain body found]'}",
            ]
        )
        return content_text
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail message: {e}")
        return f"Error getting Gmail message: {str(e)}"

@handle_http_errors("get_gmail_messages_content_batch", is_read_only=True)
async def get_gmail_messages_content_batch(
    message_ids: List[str],
    format: Literal["full", "metadata"] = "full",
) -> str:
    """
    Retrieves the content of multiple Gmail messages in a single batch request.
    Supports up to 100 messages per request using Google's batch API.

    Args:
        message_ids (List[str]): List of Gmail message IDs to retrieve (max 100).
        format (Literal["full", "metadata"]): Message format. "full" includes body, "metadata" only headers.

    Returns:
        str: A formatted list of message contents with separators.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_messages_content_batch")
        
        logger.info(
            f"[get_gmail_messages_content_batch] Invoked. Message count: {len(message_ids)}"
        )

        if not message_ids:
            raise Exception("No message IDs provided")

        output_messages = []

        # Process in chunks of 100 (Gmail batch limit)
        for chunk_start in range(0, len(message_ids), 100):
            chunk_ids = message_ids[chunk_start : chunk_start + 100]
            results: Dict[str, Dict] = {}

            def _batch_callback(request_id, response, exception):
                """Callback for batch requests"""
                results[request_id] = {"data": response, "error": exception}

            # Try to use batch API
            try:
                batch = service.new_batch_http_request(callback=_batch_callback)

                for mid in chunk_ids:
                    if format == "metadata":
                        req = (
                            service.users()
                            .messages()
                            .get(
                                userId="me",
                                id=mid,
                                format="metadata",
                                metadataHeaders=["Subject", "From"],
                            )
                        )
                    else:
                        req = (
                            service.users()
                            .messages()
                            .get(userId="me", id=mid, format="full")
                        )
                    batch.add(req, request_id=mid)

                # Execute batch request
                await asyncio.to_thread(batch.execute)

            except Exception as batch_error:
                # Fallback to asyncio.gather if batch API fails
                logger.warning(
                    f"[get_gmail_messages_content_batch] Batch API failed, falling back to asyncio.gather: {batch_error}"
                )

                async def fetch_message(mid: str):
                    try:
                        if format == "metadata":
                            msg = await asyncio.to_thread(
                                service.users()
                                .messages()
                                .get(
                                    userId="me",
                                    id=mid,
                                    format="metadata",
                                    metadataHeaders=["Subject", "From"],
                                )
                                .execute
                            )
                        else:
                            msg = await asyncio.to_thread(
                                service.users()
                                .messages()
                                .get(userId="me", id=mid, format="full")
                                .execute
                            )
                        return mid, msg, None
                    except Exception as e:
                        return mid, None, e

                # Fetch all messages in parallel
                fetch_results = await asyncio.gather(
                    *[fetch_message(mid) for mid in chunk_ids], return_exceptions=False
                )

                # Convert to results format
                for mid, msg, error in fetch_results:
                    results[mid] = {"data": msg, "error": error}

            # Process results for this chunk
            for mid in chunk_ids:
                entry = results.get(mid, {"data": None, "error": "No result"})

                if entry["error"]:
                    output_messages.append(f"⚠️ Message {mid}: {entry['error']}\n")
                else:
                    message = entry["data"]
                    if not message:
                        output_messages.append(f"⚠️ Message {mid}: No data returned\n")
                        continue

                    # Extract content based on format
                    payload = message.get("payload", {})

                    if format == "metadata":
                        headers = _extract_headers(payload, ["Subject", "From"])
                        subject = headers.get("Subject", "(no subject)")
                        sender = headers.get("From", "(unknown sender)")

                        output_messages.append(
                            f"Message ID: {mid}\n"
                            f"Subject: {subject}\n"
                            f"From: {sender}\n"
                            f"Web Link: {_generate_gmail_web_url(mid)}\n"
                        )
                    else:
                        # Full format - extract body too
                        headers = _extract_headers(payload, ["Subject", "From"])
                        subject = headers.get("Subject", "(no subject)")
                        sender = headers.get("From", "(unknown sender)")
                        body = _extract_message_body(payload)

                        output_messages.append(
                            f"Message ID: {mid}\n"
                            f"Subject: {subject}\n"
                            f"From: {sender}\n"
                            f"Web Link: {_generate_gmail_web_url(mid)}\n"
                            f"\n{body or '[No text/plain body found]'}\n"
                        )

        # Combine all messages with separators
        final_output = f"Retrieved {len(message_ids)} messages:\n\n"
        final_output += "\n---\n\n".join(output_messages)

        return final_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail messages batch: {e}")
        return f"Error getting Gmail messages batch: {str(e)}"

@handle_http_errors("send_gmail_message", is_read_only=False)
async def send_gmail_message(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
    
    Returns:
        Success message with sent message ID
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "send_gmail_message")
        
        # Create email message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send message
        sent_message = await asyncio.to_thread(
            service.users().messages().send(userId="me", body={"raw": raw_message}).execute
        )
        
        message_id = sent_message.get('id')
        return f"Email sent successfully! Message ID: {message_id}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error sending Gmail message: {e}")
        return f"Error sending Gmail message: {str(e)}"

@handle_http_errors("draft_gmail_message", is_read_only=False)
async def draft_gmail_message(
    subject: str,
    body: str,
    to: Optional[str] = None,
) -> str:
    """
    Create a draft email in Gmail.
    
    Args:
        subject: Email subject
        body: Email body content
        to: Optional recipient email address
    
    Returns:
        Success message with draft ID
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "draft_gmail_message")
        
        logger.info(f"[draft_gmail_message] Invoked. Subject: '{subject}'")

        # Prepare the email
        message = MIMEText(body)
        message["subject"] = subject

        # Add recipient if provided
        if to:
            message["to"] = to

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create a draft instead of sending
        draft_body = {"message": {"raw": raw_message}}

        # Create the draft
        created_draft = await asyncio.to_thread(
            service.users().drafts().create(userId="me", body=draft_body).execute
        )
        draft_id = created_draft.get("id")
        return f"Draft created! Draft ID: {draft_id}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error creating Gmail draft: {e}")
        return f"Error creating Gmail draft: {str(e)}"

def _format_thread_content(thread_data: dict, thread_id: str) -> str:
    """
    Helper function to format thread content from Gmail API response.

    Args:
        thread_data (dict): Thread data from Gmail API
        thread_id (str): Thread ID for display

    Returns:
        str: Formatted thread content
    """
    messages = thread_data.get("messages", [])
    if not messages:
        return f"No messages found in thread '{thread_id}'."

    # Extract thread subject from the first message
    first_message = messages[0]
    first_headers = {
        h["name"]: h["value"]
        for h in first_message.get("payload", {}).get("headers", [])
    }
    thread_subject = first_headers.get("Subject", "(no subject)")

    # Build the thread content
    content_lines = [
        f"Thread ID: {thread_id}",
        f"Subject: {thread_subject}",
        f"Messages: {len(messages)}",
        "",
    ]

    # Process each message in the thread
    for i, message in enumerate(messages, 1):
        # Extract headers
        headers = {
            h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])
        }

        sender = headers.get("From", "(unknown sender)")
        date = headers.get("Date", "(unknown date)")
        subject = headers.get("Subject", "(no subject)")

        # Extract message body
        payload = message.get("payload", {})
        body_data = _extract_message_body(payload)

        # Add message to content
        content_lines.extend(
            [
                f"=== Message {i} ===",
                f"From: {sender}",
                f"Date: {date}",
            ]
        )

        # Only show subject if it's different from thread subject
        if subject != thread_subject:
            content_lines.append(f"Subject: {subject}")

        content_lines.extend(
            [
                "",
                body_data or "[No text/plain body found]",
                "",
            ]
        )

    return "\n".join(content_lines)

@handle_http_errors("get_gmail_thread_content", is_read_only=True)
async def get_gmail_thread_content(thread_id: str) -> str:
    """
    Retrieves the complete content of a Gmail conversation thread, including all messages.

    Args:
        thread_id (str): The unique ID of the Gmail thread to retrieve.

    Returns:
        str: The complete thread content with all messages formatted for reading.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_thread_content")
        
        logger.info(f"[get_gmail_thread_content] Invoked. Thread ID: '{thread_id}'")

        # Fetch the complete thread with all messages
        thread_response = await asyncio.to_thread(
            service.users().threads().get(userId="me", id=thread_id, format="full").execute
        )

        return _format_thread_content(thread_response, thread_id)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail thread: {e}")
        return f"Error getting Gmail thread: {str(e)}"

@handle_http_errors("get_gmail_threads_content_batch", is_read_only=True)
async def get_gmail_threads_content_batch(thread_ids: List[str]) -> str:
    """
    Retrieves the content of multiple Gmail threads in a single batch request.
    Supports up to 100 threads per request using Google's batch API.

    Args:
        thread_ids (List[str]): A list of Gmail thread IDs to retrieve. The function will automatically batch requests in chunks of 100.

    Returns:
        str: A formatted list of thread contents with separators.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_threads_content_batch")
        
        logger.info(f"[get_gmail_threads_content_batch] Invoked. Thread count: {len(thread_ids)}")

        if not thread_ids:
            raise ValueError("No thread IDs provided")

        output_threads = []

        def _batch_callback(request_id, response, exception):
            """Callback for batch requests"""
            results[request_id] = {"data": response, "error": exception}

        # Process in chunks of 100 (Gmail batch limit)
        for chunk_start in range(0, len(thread_ids), 100):
            chunk_ids = thread_ids[chunk_start : chunk_start + 100]
            results: Dict[str, Dict] = {}

            # Try to use batch API
            try:
                batch = service.new_batch_http_request(callback=_batch_callback)

                for tid in chunk_ids:
                    req = service.users().threads().get(userId="me", id=tid, format="full")
                    batch.add(req, request_id=tid)

                # Execute batch request
                await asyncio.to_thread(batch.execute)

            except Exception as batch_error:
                # Fallback to asyncio.gather if batch API fails
                logger.warning(
                    f"[get_gmail_threads_content_batch] Batch API failed, falling back to asyncio.gather: {batch_error}"
                )

                async def fetch_thread(tid: str):
                    try:
                        thread = await asyncio.to_thread(
                            service.users()
                            .threads()
                            .get(userId="me", id=tid, format="full")
                            .execute
                        )
                        return tid, thread, None
                    except Exception as e:
                        return tid, None, e

                # Fetch all threads in parallel
                fetch_results = await asyncio.gather(
                    *[fetch_thread(tid) for tid in chunk_ids], return_exceptions=False
                )

                # Convert to results format
                for tid, thread, error in fetch_results:
                    results[tid] = {"data": thread, "error": error}

            # Process results for this chunk
            for tid in chunk_ids:
                entry = results.get(tid, {"data": None, "error": "No result"})

                if entry["error"]:
                    output_threads.append(f"⚠️ Thread {tid}: {entry['error']}\n")
                else:
                    thread = entry["data"]
                    if not thread:
                        output_threads.append(f"⚠️ Thread {tid}: No data returned\n")
                        continue

                    output_threads.append(_format_thread_content(thread, tid))

        # Combine all threads with separators
        header = f"Retrieved {len(thread_ids)} threads:"
        return header + "\n\n" + "\n---\n\n".join(output_threads)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail threads batch: {e}")
        return f"Error getting Gmail threads batch: {str(e)}"

@handle_http_errors("list_gmail_labels", is_read_only=True)
async def list_gmail_labels() -> str:
    """
    List all Gmail labels.
    
    Returns:
        List of Gmail labels
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "list_gmail_labels")
        
        logger.info(f"[list_gmail_labels] Invoked")

        # Get labels
        response = await asyncio.to_thread(
            service.users().labels().list(userId="me").execute
        )
        labels = response.get("labels", [])

        if not labels:
            return "No labels found."

        lines = [f"Found {len(labels)} labels:", ""]

        system_labels = []
        user_labels = []

        for label in labels:
            if label.get("type") == "system":
                system_labels.append(label)
            else:
                user_labels.append(label)

        if system_labels:
            lines.append("📂 SYSTEM LABELS:")
            for label in system_labels:
                lines.append(f"  • {label['name']} (ID: {label['id']})")
            lines.append("")

        if user_labels:
            lines.append("🏷️  USER LABELS:")
            for label in user_labels:
                lines.append(f"  • {label['name']} (ID: {label['id']})")

        return "\n".join(lines)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error listing Gmail labels: {e}")
        return f"Error listing Gmail labels: {str(e)}"

@handle_http_errors("manage_gmail_label", is_read_only=False)
async def manage_gmail_label(
    action: Literal["create", "update", "delete"],
    name: Optional[str] = None,
    label_id: Optional[str] = None,
    label_list_visibility: Literal["labelShow", "labelHide"] = "labelShow",
    message_list_visibility: Literal["show", "hide"] = "show",
) -> str:
    """
    Manages Gmail labels: create, update, or delete labels.

    Args:
        action (Literal["create", "update", "delete"]): Action to perform on the label.
        name (Optional[str]): Label name. Required for create, optional for update.
        label_id (Optional[str]): Label ID. Required for update and delete operations.
        label_list_visibility (Literal["labelShow", "labelHide"]): Whether the label is shown in the label list.
        message_list_visibility (Literal["show", "hide"]): Whether the label is shown in the message list.

    Returns:
        str: Confirmation message of the label operation.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "manage_gmail_label")
        
        logger.info(f"[manage_gmail_label] Invoked. Action: '{action}'")

        if action == "create" and not name:
            raise Exception("Label name is required for create action.")

        if action in ["update", "delete"] and not label_id:
            raise Exception("Label ID is required for update and delete actions.")

        if action == "create":
            label_object = {
                "name": name,
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility,
            }
            created_label = await asyncio.to_thread(
                service.users().labels().create(userId="me", body=label_object).execute
            )
            return f"Label created successfully!\nName: {created_label['name']}\nID: {created_label['id']}"

        elif action == "update":
            current_label = await asyncio.to_thread(
                service.users().labels().get(userId="me", id=label_id).execute
            )

            label_object = {
                "id": label_id,
                "name": name if name is not None else current_label["name"],
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility,
            }

            updated_label = await asyncio.to_thread(
                service.users()
                .labels()
                .update(userId="me", id=label_id, body=label_object)
                .execute
            )
            return f"Label updated successfully!\nName: {updated_label['name']}\nID: {updated_label['id']}"

        elif action == "delete":
            label = await asyncio.to_thread(
                service.users().labels().get(userId="me", id=label_id).execute
            )
            label_name = label["name"]

            await asyncio.to_thread(
                service.users().labels().delete(userId="me", id=label_id).execute
            )
            return f"Label '{label_name}' (ID: {label_id}) deleted successfully!"
            
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error managing Gmail label: {e}")
        return f"Error managing Gmail label: {str(e)}"

@handle_http_errors("modify_gmail_message_labels", is_read_only=False)
async def modify_gmail_message_labels(
    message_id: str,
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None,
) -> str:
    """
    Adds or removes labels from a Gmail message.

    Args:
        message_id (str): The ID of the message to modify.
        add_label_ids (Optional[List[str]]): List of label IDs to add to the message.
        remove_label_ids (Optional[List[str]]): List of label IDs to remove from the message.

    Returns:
        str: Confirmation message of the label changes applied to the message.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "modify_gmail_message_labels")
        
        logger.info(f"[modify_gmail_message_labels] Invoked. Message ID: '{message_id}'")

        if not add_label_ids and not remove_label_ids:
            raise Exception(
                "At least one of add_label_ids or remove_label_ids must be provided."
            )

        body = {}
        if add_label_ids:
            body["addLabelIds"] = add_label_ids
        if remove_label_ids:
            body["removeLabelIds"] = remove_label_ids

        await asyncio.to_thread(
            service.users().messages().modify(userId="me", id=message_id, body=body).execute
        )

        actions = []
        if add_label_ids:
            actions.append(f"Added labels: {', '.join(add_label_ids)}")
        if remove_label_ids:
            actions.append(f"Removed labels: {', '.join(remove_label_ids)}")

        return f"Message labels updated successfully!\nMessage ID: {message_id}\n{'; '.join(actions)}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error modifying Gmail message labels: {e}")
        return f"Error modifying Gmail message labels: {str(e)}"

@handle_http_errors("batch_modify_gmail_message_labels", is_read_only=False)
async def batch_modify_gmail_message_labels(
    message_ids: List[str],
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None,
) -> str:
    """
    Adds or removes labels from multiple Gmail messages in a single batch request.

    Args:
        message_ids (List[str]): A list of message IDs to modify.
        add_label_ids (Optional[List[str]]): List of label IDs to add to the messages.
        remove_label_ids (Optional[List[str]]): List of label IDs to remove from the messages.

    Returns:
        str: Confirmation message of the label changes applied to the messages.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "batch_modify_gmail_message_labels")
        
        logger.info(f"[batch_modify_gmail_message_labels] Invoked. Message IDs: '{message_ids}'")

        if not add_label_ids and not remove_label_ids:
            raise Exception(
                "At least one of add_label_ids or remove_label_ids must be provided."
            )

        body = {"ids": message_ids}
        if add_label_ids:
            body["addLabelIds"] = add_label_ids
        if remove_label_ids:
            body["removeLabelIds"] = remove_label_ids

        await asyncio.to_thread(
            service.users().messages().batchModify(userId="me", body=body).execute
        )

        actions = []
        if add_label_ids:
            actions.append(f"Added labels: {', '.join(add_label_ids)}")
        if remove_label_ids:
            actions.append(f"Removed labels: {', '.join(remove_label_ids)}")

        return f"Labels updated for {len(message_ids)} messages: {'; '.join(actions)}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error batch modifying Gmail message labels: {e}")
        return f"Error batch modifying Gmail message labels: {str(e)}"

# Register tools with the transport manager
register_tool_with_transport("search_gmail_messages", search_gmail_messages)
register_tool_with_transport("get_gmail_message_content", get_gmail_message_content)
register_tool_with_transport("get_gmail_messages_content_batch", get_gmail_messages_content_batch)
register_tool_with_transport("send_gmail_message", send_gmail_message)
register_tool_with_transport("draft_gmail_message", draft_gmail_message)
register_tool_with_transport("get_gmail_thread_content", get_gmail_thread_content)
register_tool_with_transport("get_gmail_threads_content_batch", get_gmail_threads_content_batch)
register_tool_with_transport("list_gmail_labels", list_gmail_labels)
register_tool_with_transport("manage_gmail_label", manage_gmail_label)
register_tool_with_transport("modify_gmail_message_labels", modify_gmail_message_labels)
register_tool_with_transport("batch_modify_gmail_message_labels", batch_modify_gmail_message_labels)

logger.info("Gmail tools registered with session-aware transport")