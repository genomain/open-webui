<script lang="ts">
	import { onMount } from 'svelte';

	onMount(async () => {
		// Extract the `code` and `state` query parameters from the URL
		const urlParams = new URLSearchParams(window.location.search);
		const code = urlParams.get('code');

		if (!code) {
			console.error('Missing authorization code');
			window.location.href = '/';
			return;
		}

		const state = urlParams.get('state');
		const initiatorState = localStorage.getItem('oauth_state');

		if (!state || !initiatorState) {
			console.error('Unauthorized access: Missing states');
			window.location.href = '/';
		}

		if (state !== initiatorState) {
			console.error("Unauthorized access: States don't match");
			window.location.href = '/';
		}

		const userJwt = localStorage.getItem('token');

		if (!userJwt) {
			console.error('User is not logged in.');
			window.location.href = '/';
			return;
		}

		try {
			const response = await fetch('http://localhost:8000/auth/microsoft/callback', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${userJwt}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ code })
			});

			if (!response.ok) {
				const error = await response.json();
				console.error('Failed to link Microsoft account:', error);
				return;
			}

			console.log('Microsoft account linked successfully!');
			window.location.href = '/';
		} catch (err) {
			console.error('Network or server error:', err);
		}
	});
</script>

<h1>Connecting your Microsoft account...</h1>
