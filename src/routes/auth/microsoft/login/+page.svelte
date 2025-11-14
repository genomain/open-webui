<script lang="ts">
	import { onMount } from 'svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	
	const redirectUri = `${window.location.origin}/auth/microsoft/callback`;
	
	const clientId = import.meta.env.VITE_MS_CLIENT_ID;
	const scopes = import.meta.env.VITE_MS_GRAPH_SCOPES;

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
