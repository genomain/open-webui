<script lang="ts">
	const clientId = '34b72ac9-8a31-4cf4-ac74-c03a2e6d8b9c';
	const redirectUri = 'http://localhost:5173/auth/microsoft/callback';
	const scopes = 'openid profile email offline_access User.Read Files.ReadWrite ';

	function startMicrosoftLogin() {
		const stateId = crypto.randomUUID();
		const chatRoute = 'asdf';
		const state = JSON.stringify({ stateId, chatRoute });

		// Save it locally to validate on callback
		localStorage.setItem('oauth_state', state);

		// Build the Microsoft OAuth URL
		const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(
			redirectUri
		)}&response_mode=query&scope=${encodeURIComponent(scopes)}&state=${state}`;

		// Redirect the user to Microsoft login
		window.location.href = authUrl;
	}
</script>

<h1>Login with Microsoft</h1>
<p>Click the button below to connect your Microsoft account.</p>
<button on:click={startMicrosoftLogin}> Login with Microsoft </button>

<style>
	button {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
		background-color: #0078d4;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
	}

	button:hover {
		background-color: #005a9e;
	}
</style>
