const mintButton = document.getElementById('mintButton');
const mintStatus = document.getElementById('mintStatus');

// Check if Nami wallet is available
async function isNamiAvailable() {
    return typeof window.cardano !== 'undefined' && window.cardano.nami;
}

// Enable Nami wallet
async function enableNamiWallet() {
    try {
        const nami = await window.cardano.nami.enable();
        return nami;
    } catch (error) {
        mintStatus.textContent = 'Failed to connect to Nami wallet.';
        console.error(error);
        return null;
    }
}

// Get the user's wallet address
async function getWalletAddress() {
    const nami = await enableNamiWallet();
    if (!nami) return null;

    const addresses = await nami.getUsedAddresses();
    if (addresses.length === 0) {
        mintStatus.textContent = 'No wallet address found.';
        return null;
    }
    
    // Convert Cardano Address from Base58 format
    const address = window.cardano.nami.toBech32(addresses[0]);
    return address;
}

// Minting function
async function mintToken() {
    try {
        mintStatus.textContent = 'Minting token...';

        const walletAddress = await getWalletAddress();
        if (!walletAddress) {
            mintStatus.textContent = 'Please connect to a wallet first.';
            return;
        }

        const response = await fetch('https://studio-api.nmkr.io/v2/RandomMinting/MintAndSendRandomNFT', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer <Your-API-Key>'
            },
            body: JSON.stringify({
                projectuid: '<Your-Project-UID>',
                countnft: 1,
                receiveraddress: walletAddress
            })
        });

        const result = await response.json();

        if (response.ok) {
            mintStatus.textContent = `Token minted successfully! Transaction ID: ${result.transactionId}`;
        } else {
            mintStatus.textContent = `Minting failed: ${result.message}`;
        }
    } catch (error) {
        mintStatus.textContent = `Minting error: ${error.message}`;
        console.error(error);
    }
}

// Event listener for the mint button
mintButton.addEventListener('click', async () => {
    if (await isNamiAvailable()) {
        await mintToken();
    } else {
        mintStatus.textContent = 'Nami wallet is not available. Please install it and try again.';
    }
});
