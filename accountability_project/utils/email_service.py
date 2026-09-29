"""
Transactional email helpers using the Resend SDK.

Usage:
    from utils.email_service import send_space_invite_email
    send_space_invite_email(
        to_email="user@example.com",
        invite_link="https://yourapp.com/signup?invite=<token>",
        space_name="Morning Habits",
        invited_by_username="alice",
    )
"""

import html
import logging

import resend
from django.conf import settings

logger = logging.getLogger(__name__)


def _api_key() -> str:
    """Return the Resend API key from settings, raising clearly if unset."""
    key = settings.RESEND_API_KEY
    if not key:
        raise RuntimeError(
            "RESEND_API_KEY is not configured. Set it in your environment or .env file."
        )
    return key


def send_space_invite_email(
    to_email: str,
    invite_link: str,
    space_name: str,
    invited_by_username: str,
    expiry_days: int = 7,
) -> None:
    """
    Send a space invitation email to a user who does not yet have an account.

    Raises an exception if the Resend API call fails — callers are responsible
    for catching and handling errors.
    """
    resend.api_key = _api_key()

    # Escape user-controlled values before injecting into HTML
    safe_username = html.escape(invited_by_username)
    safe_space_name = html.escape(space_name)  # kept for logging; not shown in body

    logo_url = getattr(settings, "AVIDHABITS_LOGO_URL", "")
    if logo_url:
        brand_header = (
            f'<img src="{html.escape(logo_url)}" alt="AvidHabits" '
            f'style="height: 44px; margin-bottom: 28px;" />'
        )
    else:
        brand_header = (
            '<p style="font-size: 1.5rem; font-weight: 800; color: #1976d2; '
            'letter-spacing: -0.5px; margin: 0 0 28px;">AvidHabits</p>'
        )

    html_body = f"""
    <div style="background-color: #f5f5f5; padding: 40px 16px; font-family: sans-serif;">
      <div style="background: #ffffff; max-width: 480px; margin: 0 auto;
                  border-radius: 10px; padding: 40px 40px 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">

        {brand_header}

        <h2 style="font-size: 1.35rem; font-weight: 700; color: #111; margin: 0 0 16px;">
          You&rsquo;ve been invited to AvidHabits
        </h2>

        <p style="color: #444; font-size: 0.95rem; line-height: 1.6; margin: 0 0 28px;">
          <strong>{safe_username}</strong> has invited you to join them on
          <strong>AvidHabits</strong> &mdash; the habit-tracking app that helps you
          build better habits and stay accountable.
        </p>

        <a href="{invite_link}"
           style="display: inline-block; background-color: #1976d2; color: #ffffff;
                  padding: 13px 28px; text-decoration: none; border-radius: 6px;
                  font-weight: 700; font-size: 0.95rem;">
          Accept Invitation
        </a>

        <p style="margin-top: 32px; color: #999; font-size: 0.8rem; line-height: 1.5;">
          This invitation link expires in <strong>{expiry_days} day{'s' if expiry_days != 1 else ''}</strong>.<br />
          If you weren&rsquo;t expecting this email, you can safely ignore it.
        </p>
      </div>

      <p style="text-align: center; color: #bbb; font-size: 0.75rem; margin-top: 24px;">
        &copy; {__import__('datetime').date.today().year} AvidHabits
      </p>
    </div>
    """

    params: resend.Emails.SendParams = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [to_email],
        "subject": f"{safe_username} invited you to join AvidHabits",
        "html": html_body,
    }

    result = resend.Emails.send(params)
    logger.info(
        "Invite email sent via Resend to=%s space=%s resend_id=%s",
        to_email,
        space_name,
        result.get("id"),
    )
