<script lang="ts">
	import { getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Markdown from '$lib/components/chat/Messages/Markdown.svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';
	import { settings } from '$lib/stores';

	import XMark from '$lib/components/icons/XMark.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';

	const i18n = getContext('i18n');

	const CONTENT_PREVIEW_LIMIT = 10000;
	let expandedDocs: Set<number> = new Set();

	export let show = false;
	export let citation;
	export let showPercentage = false;
	export let showRelevance = true;

	let mergedDocuments = [];
	let firstDocument: any = null;
	let isFirstDownloadable = false;

	function calculatePercentage(distance: number) {
		if (typeof distance !== 'number') return null;
		if (distance < 0) return 0;
		if (distance > 1) return 100;
		return Math.round(distance * 10000) / 100;
	}

	function getRelevanceColor(percentage: number | null) {
		if (percentage === null) return '';
		if (percentage >= 80)
			return 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200';
		if (percentage >= 60)
			return 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200';
		if (percentage >= 40)
			return 'bg-orange-200 dark:bg-orange-800 text-orange-800 dark:text-orange-200';
		return 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200';
	}

	function getRawContent(doc: any): string {
		return doc.document?.trim().replace(/\n\n+/g, '\n\n') ?? '';
	}

	function isTruncatedContent(doc: any, docIdx: number): boolean {
		const raw = getRawContent(doc);
		return (
			($settings?.renderMarkdownInPreviews ?? true) &&
			raw.length > CONTENT_PREVIEW_LIMIT &&
			!expandedDocs.has(docIdx)
		);
	}

	async function handleDownload(url: string, filename: string) {
		const token = localStorage.token;

		try {
			const response = await fetch(url, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (!response.ok) {
				console.error('Download failed', response.status);
				return;
			}

			const blob = await response.blob();
			const contentDisposition = response.headers.get('content-disposition') || '';
			const filenameMatch =
				contentDisposition.match(/filename="([^"]+)"/) ||
				contentDisposition.match(/filename=([^;]+)/);
			const resolvedFilename = filenameMatch ? filenameMatch[1].trim() : filename;

			const objectUrl = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = objectUrl;
			a.download = resolvedFilename;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(objectUrl);
		} catch (err) {
			console.error('Download error', err);
		}
	}

	$: if (citation) {
		expandedDocs = new Set();
		mergedDocuments = citation.document?.map((c, i) => {
			return {
				source: citation.source,
				document: c,
				metadata: citation.metadata?.[i],
				distance: citation.distances?.[i]
			};
		});
		if (mergedDocuments.every((doc) => doc.distance !== undefined)) {
			mergedDocuments = mergedDocuments.sort(
				(a, b) => (b.distance ?? Infinity) - (a.distance ?? Infinity)
			);
		}
		firstDocument = mergedDocuments?.[0];
		isFirstDownloadable = firstDocument?.metadata?.downloadable_file === true;
	}

	const decodeString = (str: string) => {
		try {
			return decodeURIComponent(str);
		} catch {
			return str;
		}
	};

	const getTextFragmentUrl = (doc: any): string | null => {
		const { metadata, source, document: content } = doc ?? {};
		const { file_id, page } = metadata ?? {};
		const sourceUrl = source?.url;

		const baseUrl = file_id
			? `${WEBUI_API_BASE_URL}/files/${file_id}/content${page !== undefined ? `#page=${page + 1}` : ''}`
			: sourceUrl?.includes('http')
				? sourceUrl
				: null;

		if (!baseUrl || !content) return baseUrl;

		const words = content
			.trim()
			.replace(/\s+/g, ' ')
			.split(' ')
			.filter((w: string) => w.length > 0 && !/https?:\/\/|[\u{1F300}-\u{1F9FF}]/u.test(w));

		if (words.length === 0) return baseUrl;

		const clean = (w: string) => w.replace(/[^\w]/g, '');
		const first = clean(words[0]);
		const last = clean(words.at(-1));
		const fragment = words.length === 1 ? first : `${first},${last}`;

		return fragment ? `${baseUrl}#:~:text=${fragment}` : baseUrl;
	};
</script>

<Modal size="lg" bind:show>
	<div>
		<div class="flex justify-between dark:text-gray-300 px-4.5 pt-3 pb-2">
			<div class="text-lg font-medium self-center flex items-center gap-2 grow min-w-0">
				{#if citation?.source?.name}
					{#if isFirstDownloadable}
						<span class="grow line-clamp-1">
							{decodeString(citation?.source?.name)}
						</span>
						<Tooltip
							className="w-fit shrink-0"
							content={$i18n.t('Download document')}
							placement="top"
							tippyOptions={{ duration: [500, 0] }}
						>
							<button
								on:click={() =>
									handleDownload(firstDocument.source?.url, decodeString(citation?.source?.name))}
								class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800 transition"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="size-3.5"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
									<polyline points="7 10 12 15 17 10" />
									<line x1="12" y1="15" x2="12" y2="3" />
								</svg>
								{$i18n.t('Download')}
							</button>
						</Tooltip>
					{:else if firstDocument?.metadata?.file_id || firstDocument?.source?.url?.includes('http')}
						<Tooltip
							className="w-fit"
							content={firstDocument?.source?.url?.includes('http')
								? $i18n.t('Open link')
								: $i18n.t('Open file')}
							placement="top-start"
							tippyOptions={{ duration: [500, 0] }}
						>
							<a
								class="hover:text-gray-500 dark:hover:text-gray-100 underline grow line-clamp-1"
								href={firstDocument?.metadata?.file_id
									? `${WEBUI_API_BASE_URL}/files/${firstDocument?.metadata?.file_id}/content${firstDocument?.metadata?.page !== undefined ? `#page=${firstDocument.metadata.page + 1}` : ''}`
									: firstDocument?.source?.url?.includes('http')
										? firstDocument.source.url
										: `#`}
								target="_blank"
							>
								{decodeString(citation?.source?.name)}
							</a>
						</Tooltip>
					{:else}
						{decodeString(citation?.source?.name)}
					{/if}
				{:else}
					{$i18n.t('Citation')}
				{/if}
			</div>
			<button
				class="self-center shrink-0 ml-2"
				aria-label={$i18n.t('Close citation modal')}
				on:click={() => {
					show = false;
				}}
			>
				<XMark className={'size-5'} />
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full px-5 pb-5 md:space-x-4">
			<div
				class="flex flex-col w-full dark:text-gray-200 overflow-y-scroll max-h-[22rem] scrollbar-thin gap-1"
			>
				{#each mergedDocuments as document, documentIdx}
					<div class="flex flex-col w-full gap-2">
						{#if document.metadata?.parameters}
							<div>
								<div class="text-sm font-medium dark:text-gray-300 mb-1">
									{$i18n.t('Parameters')}
								</div>
								<Textarea readonly value={JSON.stringify(document.metadata.parameters, null, 2)} />
							</div>
						{/if}

						{#if document?.metadata?.downloadable_file === true}
							<!-- Source metadata -->
							<div>
								<div class="text-sm text-gray-600 dark:text-gray-400 flex flex-col gap-1">
									{#if document.metadata?.chunk_index !== undefined}
										<div class="flex items-center gap-2">
											<span class="font-medium dark:text-gray-300">{$i18n.t('Chunk')}:</span>
											<span>{document.metadata.chunk_index}</span>
										</div>
									{/if}
									{#if document.metadata?.relevance !== undefined}
										<div class="flex items-center gap-2">
											<span class="font-medium dark:text-gray-300">{$i18n.t('Relevance')}:</span>
											<span class="text-gray-500 dark:text-gray-500"
												>{document.metadata.relevance}</span
											>
										</div>
									{/if}
								</div>
							</div>

							<!-- Chunk excerpt -->
							{#if document.document?.trim()}
								<div>
									{#if $settings?.renderMarkdownInPreviews ?? true}
										<div class="text-sm prose dark:prose-invert max-w-full">
											<Markdown
												content={isTruncatedContent(document, documentIdx)
													? getRawContent(document).slice(0, CONTENT_PREVIEW_LIMIT)
													: getRawContent(document)}
												id="citation-{documentIdx}"
											/>
										</div>
										{#if isTruncatedContent(document, documentIdx)}
											<button
												class="mt-1 text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition"
												on:click={() => {
													expandedDocs.add(documentIdx);
													expandedDocs = expandedDocs;
												}}
											>
												{$i18n.t('Show all ({{COUNT}} characters)', {
													COUNT: getRawContent(document).length.toLocaleString()
												})}
											</button>
										{/if}
									{:else}
										<pre class="text-sm dark:text-gray-400 whitespace-pre-line">{getRawContent(
												document
											)}</pre>
									{/if}
								</div>
							{/if}
							<hr class="border-t dark:border-gray-700 my-2" />
						{:else}
							<!-- Standard citation content -->
							<div>
								<div
									class="text-sm font-medium dark:text-gray-300 flex items-center gap-2 w-fit mb-1"
								>
									{#if document.source?.url?.includes('http')}
										{#if getTextFragmentUrl(document)}
											<a
												href={getTextFragmentUrl(document)}
												target="_blank"
												class="underline hover:text-gray-500 dark:hover:text-gray-100"
												>{$i18n.t('Content')}</a
											>
										{:else}
											{$i18n.t('Content')}
										{/if}
									{:else}
										{$i18n.t('Content')}
									{/if}

									{#if showRelevance && document.distance !== undefined}
										<Tooltip
											className="w-fit"
											content={$i18n.t('Relevance')}
											placement="top-start"
											tippyOptions={{ duration: [500, 0] }}
										>
											<div class="text-sm my-1 dark:text-gray-400 flex items-center gap-2 w-fit">
												{#if showPercentage}
													{#if typeof calculatePercentage(document.distance) === 'number'}
														<span
															class={`px-1 rounded-sm font-medium ${getRelevanceColor(calculatePercentage(document.distance))}`}
														>
															{calculatePercentage(document.distance)?.toFixed(2)}%
														</span>
													{/if}
												{:else if typeof document?.distance === 'number'}
													<span class="text-gray-500 dark:text-gray-500">
														({(document?.distance ?? 0).toFixed(4)})
													</span>
												{/if}
											</div>
										</Tooltip>
									{/if}

									{#if Number.isInteger(document?.metadata?.page)}
										<span class="text-sm text-gray-500 dark:text-gray-400">
											({$i18n.t('page')}
											{document.metadata.page + 1})
										</span>
									{/if}
								</div>

								{#if document.metadata?.html}
									<iframe
										class="w-full border-0 h-auto rounded-none"
										sandbox="allow-scripts allow-forms{($settings?.iframeSandboxAllowSameOrigin ??
										false)
											? ' allow-same-origin'
											: ''}"
										srcdoc={document.document}
										title={$i18n.t('Content')}
									></iframe>
								{:else if $settings?.renderMarkdownInPreviews ?? true}
									<div class="text-sm prose dark:prose-invert max-w-full">
										<Markdown
											content={isTruncatedContent(document, documentIdx)
												? getRawContent(document).slice(0, CONTENT_PREVIEW_LIMIT)
												: getRawContent(document)}
											id="citation-{documentIdx}"
										/>
									</div>
									{#if isTruncatedContent(document, documentIdx)}
										<button
											class="mt-1 text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition"
											on:click={() => {
												expandedDocs.add(documentIdx);
												expandedDocs = expandedDocs;
											}}
										>
											{$i18n.t('Show all ({{COUNT}} characters)', {
												COUNT: getRawContent(document).length.toLocaleString()
											})}
										</button>
									{/if}
								{:else}
									<pre class="text-sm dark:text-gray-400 whitespace-pre-line">{getRawContent(
											document
										)}</pre>
								{/if}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	</div>
</Modal>
