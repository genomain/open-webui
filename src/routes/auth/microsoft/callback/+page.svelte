<script lang="ts">
	import Spinner from '$lib/components/common/Spinner.svelte';
	import { onMount } from 'svelte';

	const MCP_API_BASE = import.meta.env.VITE_GENOMAIN_API_URL;

	let loading = true;
	let success = false;
	let error: string | null = null;

	async function handleClose() {
		// Try closing the window — works only if opened by script
		window.close();

		if (!window.closed) {
			alert('Please close this tab manually.');
		}
	}

	onMount(async () => {
		try {
			const urlParams = new URLSearchParams(window.location.search);
			const code = urlParams.get('code');
			const state = urlParams.get('state');
			const initiatorState = localStorage.getItem('oauth_state');
			const userJwt = localStorage.getItem('token');

			if (!code) throw new Error('Missing authorization code');
			if (!state || !initiatorState) throw new Error('Missing state');
			if (state !== initiatorState) throw new Error('State mismatch');
			if (!userJwt) throw new Error('User not logged in');

			const response = await fetch(`${MCP_API_BASE}/auth/microsoft/callback`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${userJwt}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ code })
			});

			if (!response.ok) {
				const errorJson = await response.json().catch(() => ({}));
				throw new Error(errorJson.detail || 'Failed to link Microsoft account');
			}

			success = true;
		} catch (err) {
			console.error(err);
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
			localStorage.setItem('oauth_state', '');
		}
	});
</script>

{#if loading}
	<Spinner />
{:else}
	<div class="flex flex-col gap-2 align-center items-center">
		<h1>
			{success
				? 'Microsoft account linked successfully!'
				: 'Something went wrong, please try again'}
		</h1>
		<button
			aria-labelledby="get-started"
			class="relative z-20 flex p-3 rounded-full bg-white/5 hover:bg-white/10 transition font-medium text-sm"
			on:click={handleClose}
		>
			Close tab
		</button>
	</div>
{/if}
