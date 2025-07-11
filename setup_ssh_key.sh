#!/bin/bash

# SSH Key Setup Script for macstadium Mac Machines
# Sets up passwordless SSH access using a private key (.pem) from the setup directory
# Extracts public key from private key, sets up SSH, and deletes private key for security
# Similar to EC2 instance setup

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "SSH Key Setup for macstadium Mac Machine"
echo "=========================================="
echo ""

# Get current user
CURRENT_USER=$(whoami)
USER_HOME="$HOME"
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}👤 Current user: $CURRENT_USER${NC}"
echo -e "${BLUE}🏠 User home: $USER_HOME${NC}"
echo -e "${BLUE}📁 Setup directory: $SETUP_DIR${NC}"
echo ""

# Look for private key files (.pem) in the setup directory
echo -e "${BLUE}🔍 Looking for private key files (.pem)...${NC}"

PRIVATE_KEY_FILE=""
POSSIBLE_KEYS=(
    "$SETUP_DIR/id_rsa.pem"
    "$SETUP_DIR/id_ed25519.pem"
    "$SETUP_DIR/id_ecdsa.pem"
    "$SETUP_DIR/key.pem"
    "$SETUP_DIR/ssh_key.pem"
    "$SETUP_DIR/macstadium.pem"
)

for key_file in "${POSSIBLE_KEYS[@]}"; do
    if [ -f "$key_file" ]; then
        PRIVATE_KEY_FILE="$key_file"
        echo -e "${GREEN}✅ Found private key: $key_file${NC}"
        break
    fi
done

# If no standard key found, look for any .pem file
if [ -z "$PRIVATE_KEY_FILE" ]; then
    echo -e "${YELLOW}⚠️  No standard private key found, searching for any .pem file...${NC}"
    
    PEM_FILES=($(find "$SETUP_DIR" -maxdepth 1 -name "*.pem" -type f 2>/dev/null))
    
    if [ ${#PEM_FILES[@]} -eq 1 ]; then
        PRIVATE_KEY_FILE="${PEM_FILES[0]}"
        echo -e "${GREEN}✅ Found private key: $PRIVATE_KEY_FILE${NC}"
    elif [ ${#PEM_FILES[@]} -gt 1 ]; then
        echo -e "${YELLOW}⚠️  Multiple .pem files found:${NC}"
        for i in "${!PEM_FILES[@]}"; do
            echo "  $((i+1))) ${PEM_FILES[$i]}"
        done
        echo ""
        read -p "Select which private key to use (1-${#PEM_FILES[@]}): " choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#PEM_FILES[@]}" ]; then
            PRIVATE_KEY_FILE="${PEM_FILES[$((choice-1))]}"
            echo -e "${GREEN}✅ Selected: $PRIVATE_KEY_FILE${NC}"
        else
            echo -e "${RED}❌ Invalid choice${NC}"
            exit 1
        fi
    fi
fi

# If still no key found, prompt for manual path
if [ -z "$PRIVATE_KEY_FILE" ]; then
    echo -e "${RED}❌ No private key file found in $SETUP_DIR${NC}"
    echo ""
    echo "Please ensure you have a private key file (.pem) in the setup directory."
    echo "Expected files: id_rsa.pem, id_ed25519.pem, key.pem, etc."
    echo ""
    read -p "Enter the full path to your private key file: " PRIVATE_KEY_FILE
    
    if [ ! -f "$PRIVATE_KEY_FILE" ]; then
        echo -e "${RED}❌ File not found: $PRIVATE_KEY_FILE${NC}"
        exit 1
    fi
fi

# Validate the private key format and extract public key
echo -e "${BLUE}🔍 Validating private key and extracting public key...${NC}"

# Check file type and permissions
echo -e "${BLUE}📋 File information:${NC}"
echo "  File: $PRIVATE_KEY_FILE"
echo "  Type: $(file "$PRIVATE_KEY_FILE")"
echo "  Permissions: $(ls -la "$PRIVATE_KEY_FILE")"
echo "  Size: $(wc -c < "$PRIVATE_KEY_FILE") bytes"

# Check if file starts with expected private key header
if head -1 "$PRIVATE_KEY_FILE" | grep -q "BEGIN.*PRIVATE KEY"; then
    echo -e "${GREEN}✅ File appears to be a private key${NC}"
else
    echo -e "${YELLOW}⚠️  File may not be a standard private key format${NC}"
    echo "  First line: $(head -1 "$PRIVATE_KEY_FILE")"
fi

# Set proper permissions on private key file
chmod 600 "$PRIVATE_KEY_FILE"

# Test key validation with detailed error output
echo -e "${BLUE}🔍 Testing key validation...${NC}"
if ssh-keygen -l -f "$PRIVATE_KEY_FILE" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Valid private key format${NC}"
    
    # Extract public key from private key
    echo -e "${BLUE}🔑 Extracting public key from private key...${NC}"
    PUBLIC_KEY_CONTENT=$(ssh-keygen -y -f "$PRIVATE_KEY_FILE" 2>/dev/null)
    
    if [ -z "$PUBLIC_KEY_CONTENT" ]; then
        echo -e "${RED}❌ Failed to extract public key from private key${NC}"
        echo "  This might indicate the key is encrypted with a passphrase"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Successfully extracted public key${NC}"
else
    echo -e "${RED}❌ Invalid private key format${NC}"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "  1. Check if this is actually an SSH private key"
    echo "  2. Verify the file isn't corrupted"
    echo "  3. Check if the key requires a passphrase"
    echo "  4. Ensure proper file permissions (600)"
    echo ""
    echo "💡 Run manually to debug:"
    echo "  ssh-keygen -l -f \"$PRIVATE_KEY_FILE\""
    echo "  ssh-keygen -y -f \"$PRIVATE_KEY_FILE\""
    exit 1
fi

# Create .ssh directory if it doesn't exist
SSH_DIR="$USER_HOME/.ssh"
echo -e "${BLUE}📁 Setting up SSH directory...${NC}"

if [ ! -d "$SSH_DIR" ]; then
    mkdir -p "$SSH_DIR"
    echo -e "${GREEN}✅ Created $SSH_DIR${NC}"
else
    echo -e "${GREEN}✅ SSH directory exists${NC}"
fi

# Set proper permissions on .ssh directory
chmod 700 "$SSH_DIR"

# Set up authorized_keys
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"

echo -e "${BLUE}🔑 Setting up authorized keys...${NC}"

# Check if the key already exists
if [ -f "$AUTHORIZED_KEYS" ] && grep -Fxq "$PUBLIC_KEY_CONTENT" "$AUTHORIZED_KEYS"; then
    echo -e "${YELLOW}⚠️  Public key already exists in authorized_keys${NC}"
else
    # Add the public key to authorized_keys
    echo "$PUBLIC_KEY_CONTENT" >> "$AUTHORIZED_KEYS"
    echo -e "${GREEN}✅ Added public key to authorized_keys${NC}"
fi

# Set proper permissions on authorized_keys
chmod 600 "$AUTHORIZED_KEYS"

# Display key fingerprint for verification
echo -e "${BLUE}🔍 Key fingerprint:${NC}"
ssh-keygen -l -f "$PRIVATE_KEY_FILE"

echo ""

# Delete the private key file for security
echo -e "${BLUE}🗑️  Deleting private key file for security...${NC}"
if rm -f "$PRIVATE_KEY_FILE"; then
    echo -e "${GREEN}✅ Private key file deleted: $(basename "$PRIVATE_KEY_FILE")${NC}"
else
    echo -e "${YELLOW}⚠️  Could not delete private key file: $PRIVATE_KEY_FILE${NC}"
fi

echo ""

# Set up passwordless sudo
echo -e "${BLUE}🔐 Setting up passwordless sudo...${NC}"

SUDOERS_FILE="/etc/sudoers.d/99-$CURRENT_USER-nopasswd"

# Check if already configured
if sudo test -f "$SUDOERS_FILE"; then
    echo -e "${YELLOW}⚠️  Passwordless sudo already configured${NC}"
else
    # Create sudoers file for passwordless sudo
    echo "$CURRENT_USER ALL=(ALL) NOPASSWD: ALL" | sudo tee "$SUDOERS_FILE" >/dev/null
    
    # Set proper permissions
    sudo chmod 440 "$SUDOERS_FILE"
    
    echo -e "${GREEN}✅ Configured passwordless sudo${NC}"
fi

# Check SSH daemon configuration
echo -e "${BLUE}🔧 Checking SSH daemon configuration...${NC}"

SSHD_CONFIG="/etc/ssh/sshd_config"
RESTART_SSHD=false

# Check if PubkeyAuthentication is enabled
if ! sudo grep -q "^PubkeyAuthentication yes" "$SSHD_CONFIG"; then
    echo -e "${YELLOW}⚠️  Enabling PubkeyAuthentication in sshd_config${NC}"
    
    # Backup original config
    sudo cp "$SSHD_CONFIG" "$SSHD_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Enable PubkeyAuthentication (cross-platform sed)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS (BSD sed)
        SED_INPLACE=(-i '')
    else
        # Linux (GNU sed)
        SED_INPLACE=(-i)
    fi
    
    if sudo grep -q "^#PubkeyAuthentication" "$SSHD_CONFIG"; then
        sudo sed "${SED_INPLACE[@]}" 's/^#PubkeyAuthentication.*/PubkeyAuthentication yes/' "$SSHD_CONFIG"
    elif sudo grep -q "^PubkeyAuthentication" "$SSHD_CONFIG"; then
        sudo sed "${SED_INPLACE[@]}" 's/^PubkeyAuthentication.*/PubkeyAuthentication yes/' "$SSHD_CONFIG"
    else
        echo "PubkeyAuthentication yes" | sudo tee -a "$SSHD_CONFIG" >/dev/null
    fi
    
    RESTART_SSHD=true
fi

# Restart SSH daemon if needed
if [ "$RESTART_SSHD" = true ]; then
    echo -e "${BLUE}🔄 Restarting SSH daemon...${NC}"
    sudo launchctl unload /System/Library/LaunchDaemons/ssh.plist 2>/dev/null || true
    sudo launchctl load /System/Library/LaunchDaemons/ssh.plist
    echo -e "${GREEN}✅ SSH daemon restarted${NC}"
else
    echo -e "${GREEN}✅ SSH daemon configuration is correct${NC}"
fi

echo ""
echo "=========================================="
echo "✅ SSH Key Setup Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}🎉 SSH key setup completed successfully!${NC}"
echo ""
echo "📋 What was configured:"
echo "  • Public key extracted from private key and added to ~/.ssh/authorized_keys"
echo "  • Private key file deleted for security"
echo "  • Passwordless sudo enabled for user: $CURRENT_USER"
echo "  • SSH daemon configured for public key authentication"
echo "  • Proper file permissions set"
echo ""
echo "🔍 Connection details:"
echo "  • SSH to this machine: ssh $CURRENT_USER@$(hostname)"
echo "  • IP Address: $(ifconfig | grep -E 'inet.*broadcast' | awk '{print $2}' | head -1)"
echo "  • Key fingerprint: $(echo "$PUBLIC_KEY_CONTENT" | ssh-keygen -l -f - | awk '{print $2}')"
echo ""
echo "🧪 Test connection:"
echo "  1. From your client machine, use: ssh $CURRENT_USER@$(hostname)"
echo "  2. No password should be required"
echo "  3. Test sudo: sudo whoami (should not ask for password)"
echo "" 