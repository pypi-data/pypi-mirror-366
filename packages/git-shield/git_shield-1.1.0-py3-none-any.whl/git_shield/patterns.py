import re

patterns = {
    # AWS
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"[0-9a-zA-Z/+]{40}",
    "AWS Session Token": r"FQoGZXIvYXdz[0-9a-zA-Z/+]{200,}",
    
    # Private/Public Keys
    "Private Key": r"-----BEGIN PRIVATE KEY-----",
    "RSA Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
    "DSA Private Key": r"-----BEGIN DSA PRIVATE KEY-----",
    "EC Private Key": r"-----BEGIN EC PRIVATE KEY-----",
    "Public Key": r"-----BEGIN PUBLIC KEY-----",
    "SSH Private Key": r"-----BEGIN OPENSSH PRIVATE KEY-----",
    "SSH Public Key": r"ssh-rsa|ssh-dss|ssh-ed25519",
    
    # Passwords and Credentials
    "Password": r"password\s*=\s*['\"][^'\"]+['\"]",
    "Password (colon)": r"password\s*:\s*['\"][^'\"]+['\"]",
    "Secret": r"secret\s*=\s*['\"][^'\"]+['\"]",
    "Secret Key": r"secret_key\s*=\s*['\"][^'\"]+['\"]",
    "API Secret": r"api_secret\s*=\s*['\"][^'\"]+['\"]",
    
    # API Keys
    "API Key": r"api_key\s*=\s*['\"][^'\"]+['\"]",
    "API Token": r"api_token\s*=\s*['\"][^'\"]+['\"]",
    "Access Token": r"access_token\s*=\s*['\"][^'\"]+['\"]",
    "Bearer Token": r"bearer\s+[a-zA-Z0-9._-]+",
    
    # GitHub
    "GitHub Personal Access Token": r"ghp_[0-9a-zA-Z]{36}",
    "GitHub OAuth Token": r"gho_[0-9a-zA-Z]{36}",
    "GitHub App Token": r"ghu_[0-9a-zA-Z]{36}",
    "GitHub Refresh Token": r"ghr_[0-9a-zA-Z]{36}",
    
    # JWT Tokens
    "JWT Token": r"eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
    
    # Database
    "Database URL": r"(postgresql|mysql|mongodb|redis)://[^@]+@[^:]+:[0-9]+/[^?\s]+",
    
    # OAuth
    "OAuth Client ID": r"client_id\s*=\s*['\"][^'\"]+['\"]",
    "OAuth Client Secret": r"client_secret\s*=\s*['\"][^'\"]+['\"]",
    "OAuth Token": r"oauth_token\s*=\s*['\"][^'\"]+['\"]",
    
    # Slack
    "Slack Token": r"xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
    
    # Stripe
    "Stripe Live Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Stripe Test Key": r"sk_test_[0-9a-zA-Z]{24}",
    "Stripe Publishable Live Key": r"pk_live_[0-9a-zA-Z]{24}",
    "Stripe Publishable Test Key": r"pk_test_[0-9a-zA-Z]{24}",
    
    # Google
    "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Google OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    
    # Facebook
    "Facebook Access Token": r"EAACEdEose0cBA[0-9A-Za-z]+",
    
    # Twitter
    "Twitter API Key": r"[1-9][0-9]+-[0-9a-zA-Z]{40}",
    "Twitter Bearer Token": r"AAAA[0-9A-Za-z\\-_]{140}",
    
    # Twilio
    "Twilio API Key": r"SK[0-9a-fA-F]{32}",
    "Twilio Account SID": r"AC[a-zA-Z0-9]{32}",
    "Twilio Auth Token": r"[0-9a-fA-F]{32}",
    
    # SendGrid
    "SendGrid API Key": r"SG\.[0-9A-Za-z\\-_]{22}\.[0-9A-Za-z\\-_]{43}",
    
    # Mailgun
    "Mailgun API Key": r"key-[0-9a-zA-Z]{32}",
    
    # Firebase
    "Firebase URL": r".*firebaseio\.com",
    
    # Heroku
    "Heroku API Key": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    
    # Comments with potential secrets
    "Secret in Comment": r"//.*(password|secret|key|token)\s*[:=]\s*[^\s]+",
    "Secret in Comment (hash)": r"#.*(password|secret|key|token)\s*[:=]\s*[^\s]+",
    "Secret in Comment (block)": r"/\*.*(password|secret|key|token)\s*[:=]\s*[^\s]+.*\*/",
}


def load_patterns() -> dict:
    """
    Load patterns from a predefined dictionary.

    Returns:
        dict: A dictionary containing various patterns.
    """
    compiled_patterns = {}
    for pattern_name, regex in patterns.items():
        compiled_regex = re.compile(regex, re.IGNORECASE | re.MULTILINE)
        compiled_patterns[pattern_name] = compiled_regex
    return compiled_patterns
