/**
 * NFT Ownership Verification
 * Verifies Sandbox avatar NFT ownership on Polygon using ethers.js and WalletConnect
 */

const { ethers } = require("ethers");

// Polygon mainnet RPC endpoints
const POLYGON_RPC_URLS = [
  "https://polygon-rpc.com",
  "https://rpc-mainnet.matic.network",
  "https://matic-mainnet.chainstacklabs.com",
];

// ERC-721 ABI (minimal interface for ownership checking)
const ERC721_ABI = [
  "function ownerOf(uint256 tokenId) view returns (address owner)",
  "function balanceOf(address owner) view returns (uint256 balance)",
  "function tokenOfOwnerByIndex(address owner, uint256 index) view returns (uint256 tokenId)",
  "function totalSupply() view returns (uint256)",
  "function name() view returns (string)",
  "function symbol() view returns (string)",
];

/**
 * Verify NFT ownership on Polygon
 * @param {string} contractAddress - The NFT contract address
 * @param {string} tokenId - The token ID to check
 * @param {string} walletAddress - The wallet address to verify (optional)
 * @returns {Promise<boolean>} - True if wallet owns the NFT
 */
async function verifyNFTOwnership(
  contractAddress,
  tokenId,
  walletAddress = null
) {
  try {
    // Create provider with fallback RPC URLs
    let provider = null;
    for (const rpcUrl of POLYGON_RPC_URLS) {
      try {
        provider = new ethers.JsonRpcProvider(rpcUrl);
        // Test the connection
        await provider.getBlockNumber();
        console.log(`Connected to Polygon via: ${rpcUrl}`);
        break;
      } catch (error) {
        console.log(`Failed to connect to ${rpcUrl}, trying next...`);
        continue;
      }
    }

    if (!provider) {
      throw new Error("Could not connect to Polygon network");
    }

    // Create contract instance
    const contract = new ethers.Contract(contractAddress, ERC721_ABI, provider);

    // Get contract info
    try {
      const name = await contract.name();
      const symbol = await contract.symbol();
      console.log(`Contract: ${name} (${symbol})`);
    } catch (error) {
      console.log(
        "Could not fetch contract metadata (contract may not be ERC-721 compliant)"
      );
    }

    // If no wallet address provided, try to connect via WalletConnect
    if (!walletAddress) {
      console.log(
        "No wallet address provided. In a full implementation, this would trigger WalletConnect..."
      );
      console.log(
        "For now, please provide a wallet address using the --wallet parameter"
      );
      return false;
    }

    // Validate addresses
    if (!ethers.isAddress(contractAddress)) {
      throw new Error("Invalid contract address format");
    }

    if (!ethers.isAddress(walletAddress)) {
      throw new Error("Invalid wallet address format");
    }

    console.log(
      `Checking ownership of token ${tokenId} for wallet ${walletAddress}...`
    );

    // Check who owns the specific token
    const owner = await contract.ownerOf(tokenId);
    console.log(`Token ${tokenId} is owned by: ${owner}`);

    // Compare addresses (case-insensitive)
    const ownsToken = owner.toLowerCase() === walletAddress.toLowerCase();

    if (ownsToken) {
      console.log("SUCCESS: Ownership verified");
      return true;
    } else {
      console.log("FAILED: Wallet does not own this token");
      return false;
    }
  } catch (error) {
    if (error.message.includes("ERC721: invalid token ID")) {
      console.log("FAILED: Token ID does not exist");
    } else if (error.message.includes("execution reverted")) {
      console.log(
        "FAILED: Contract call failed - token may not exist or contract may not be ERC-721"
      );
    } else {
      console.log(`Error: ${error.message}`);
    }
    return false;
  }
}

/**
 * Get all tokens owned by a wallet (useful for discovery)
 * @param {string} contractAddress - The NFT contract address
 * @param {string} walletAddress - The wallet address
 * @returns {Promise<string[]>} - Array of token IDs owned by the wallet
 */
async function getOwnedTokens(contractAddress, walletAddress) {
  try {
    const provider = new ethers.JsonRpcProvider(POLYGON_RPC_URLS[0]);
    const contract = new ethers.Contract(contractAddress, ERC721_ABI, provider);

    const balance = await contract.balanceOf(walletAddress);
    console.log(`Wallet ${walletAddress} owns ${balance} tokens`);

    const tokenIds = [];
    for (let i = 0; i < balance; i++) {
      try {
        const tokenId = await contract.tokenOfOwnerByIndex(walletAddress, i);
        tokenIds.push(tokenId.toString());
      } catch (error) {
        console.log(`Could not fetch token at index ${i}:`, error.message);
      }
    }

    return tokenIds;
  } catch (error) {
    console.log(`Error fetching owned tokens: ${error.message}`);
    return [];
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.log(
      "Usage: node verify_owner.js <contract_address> <token_id> [wallet_address]"
    );
    console.log("");
    console.log("Examples:");
    console.log("  node verify_owner.js 0x... 123 0x...");
    console.log(
      "  node verify_owner.js 0x... 123  # Will prompt for WalletConnect"
    );
    process.exit(1);
  }

  const [contractAddress, tokenId, walletAddress] = args;

  try {
    const result = await verifyNFTOwnership(
      contractAddress,
      tokenId,
      walletAddress
    );

    // Output result for CLI parsing (Python subprocess)
    console.log(result);
    process.exit(result ? 0 : 1);
  } catch (error) {
    console.error("Verification failed:", error.message);
    process.exit(1);
  }
}

// WalletConnect integration (placeholder for future implementation)
async function connectWallet() {
  // TODO: Implement WalletConnect v2 integration
  // This would handle wallet connection UI and return the connected address
  console.log("WalletConnect integration not yet implemented");
  console.log("Please provide wallet address manually for now");
  return null;
}

// Export functions for potential module usage
module.exports = {
  verifyNFTOwnership,
  getOwnedTokens,
  connectWallet,
};

// Run CLI if called directly
if (require.main === module) {
  main().catch(console.error);
}
