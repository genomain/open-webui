<script lang="ts">
	import { onMount } from 'svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const clientId = '34b72ac9-8a31-4cf4-ac74-c03a2e6d8b9c';
	const redirectUri = 'http://localhost:5173/auth/microsoft/callback';
	const scopes = 'openid profile email offline_access User.Read Files.ReadWrite ';

	function startMicrosoftLogin() {
		const stateId = crypto.randomUUID();

		const state = JSON.stringify({ stateId });

		// Save it locally to validate on callback
		localStorage.setItem('oauth_state', state);

		// Build the Microsoft OAuth URL
		const authUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(
			redirectUri
		)}&response_mode=query&scope=${encodeURIComponent(scopes)}&state=${state}`;

		// Redirect the user to Microsoft login
		window.location.href = authUrl;
	}

	onMount(async () => {
		startMicrosoftLogin();
	});
</script>

<Spinner />
