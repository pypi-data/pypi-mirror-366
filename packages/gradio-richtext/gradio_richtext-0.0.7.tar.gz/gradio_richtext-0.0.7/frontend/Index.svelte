<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { BlockTitle } from "@gradio/atoms";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { onMount, onDestroy } from "svelte";
    import { BlockNoteEditor } from "@blocknote/core";

	export let gradio: Gradio<{
		change: never;
		input: never;
		clear_status: LoadingStatus;
	}>;
	export let label = "Rich Text Editor";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let value = "";
	export let show_label: boolean;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus | undefined = undefined;
	export let value_is_output = false;
	export let interactive: boolean;

	let element: HTMLElement;
	let editor: BlockNoteEditor;

	function handleKeydown(event: KeyboardEvent) {
		if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
			event.preventDefault();
			const selectedText = editor.getSelectedText();
			const existingUrl = editor.getSelectedLinkUrl();
			
			const url = prompt('Enter URL:', existingUrl || 'https://');
			
			if (url && url.trim()) {
				let finalUrl = url.trim();
				if (!/^https?:\/\//i.test(finalUrl)) {
					finalUrl = 'https://' + finalUrl;
				}
				
				editor.createLink(finalUrl, selectedText || undefined);
			}
			
			editor.focus();
		}
	}


	onMount(() => {
		editor = BlockNoteEditor.create({
			uploadFile: async (file: any) => {
				return new Promise((resolve) => {
					const reader = new FileReader();
					reader.onload = () => {
						resolve(reader.result as string);
					};
					reader.readAsDataURL(file);
				});
			},
			placeholders: {
				default: "",
				emptyDocument: "Write something...",
				bulletListItem: "",
				numberedListItem: "",
				checkListItem: "",
				toggleListItem: ""
			}
		});
		editor.mount(element);
		
		element.addEventListener('keydown', handleKeydown);
		
		editor.onChange(async () => {
			let rawValue = await editor.blocksToMarkdownLossy(editor.document);
			value = rawValue.replace(/\n+$/, '').replace(/^\n+/, '').trim();
			console.log('Editor onChange - final value:', JSON.stringify(value));
			gradio.dispatch("change");
			if (!value_is_output) {
				gradio.dispatch("input");
			}
		});
	
	});

	onDestroy(() => {
		if (element) {
			element.removeEventListener('keydown', handleKeydown);
		}
	});

	$: if (editor && value !== undefined) {
		updateEditorFromValue();
	}

	async function updateEditorFromValue() {
		if (!editor) return;
		
		const currentMarkdown = await editor.blocksToMarkdownLossy(editor.document);
		
		if (currentMarkdown !== value) {
			const blocksFromMarkdown = await editor.tryParseMarkdownToBlocks(value || "");
			editor.replaceBlocks(editor.document, blocksFromMarkdown);
		}
	}

	$: if (editor) {
		editor.isEditable = interactive;
	}

	$: if (value === null) value = "";

</script>

<Block
	{visible}
	{elem_id}
	{elem_classes}
	{scale}
	{min_width}
	allow_overflow={false}
	padding={true}
>
	{#if loading_status}
		<StatusTracker
			autoscroll={gradio.autoscroll}
			i18n={gradio.i18n}
			{...loading_status}
			on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
		/>
	{/if}

	<div class="container">
		<BlockTitle {show_label} info={undefined}>{label}</BlockTitle>

		<div
			bind:this={element}
			class="editor"
			data-disabled={!interactive}
		/>
	</div>
</Block>

<style>
	.container {
		display: block;
		width: 100%;
	}

	.editor {
		display: block;
		position: relative;
		width: 100%;
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
		min-height: 2.5em;
		background: var(--input-background-fill);
		font-family: var(--font);
		font-size: var(--input-text-size);
		color: var(--body-text-color);
	}

	.editor:focus-within {
		box-shadow: var(--input-shadow-focus);
		border-color: var(--input-border-color-focus);
	}

	/* BlockNote editor integration */
	.editor :global(.bn-editor) {
		background: transparent;
		font-family: inherit;
		font-size: inherit;
		color: inherit;
		line-height: 1
	}

	/* BlockNote content styling */
	.editor :global(.bn-block-content) {
		margin: 0.25em 0;
		padding: 0.25em 0.5em;
	}

	.editor :global(.bn-block-content p) {
		margin: 0;
		line-height: 1
	}

	/* BlockNote heading styles */
	.editor :global(.bn-block-content h1),
	.editor :global(.bn-block-content h2),
	.editor :global(.bn-block-content h3) {
		font-weight: 600;
		margin: 0.5em 0 0.25em 0;
		color: var(--body-text-color);
	}

	.editor :global(.bn-block-content h1) { font-size: 1.5em; }
	.editor :global(.bn-block-content h2) { font-size: 1.25em; }
	.editor :global(.bn-block-content h3) { font-size: 1.1em; }

	/* BlockNote bullet list items */
	.editor :global([data-content-type="bulletListItem"]) {
		display: list-item;
		list-style-type: disc;
		margin-left: 2em;
		padding-left: 0.5em;
	}

	/* BlockNote numbered list items */
	.editor :global([data-content-type="numberedListItem"]) {
		display: list-item;
		list-style-type: decimal;
		margin-left: 2em;
		padding-left: 0.5em;
	}

	/* Ensure list content displays properly */
	.editor :global([data-content-type="bulletListItem"] .bn-block-content),
	.editor :global([data-content-type="numberedListItem"] .bn-block-content) {
		display: inline;
	}

	/* BlockNote check list styling */
	.editor :global([data-content-type="checkListItem"]) {
		display: flex;
		align-items: flex-start;
		gap: 0.5em;
	}

	.editor :global([data-content-type="checkListItem"] input[type="checkbox"]) {
		margin-top: 0.2em;
		cursor: pointer;
	}

	/* BlockNote toggle list styling */
	.editor :global([data-content-type="toggleListItem"]) {
		border-left: 2px solid var(--input-border-color);
		padding-left: 0.75em;
		margin: 0.25em 0;
	}

	.editor :global([data-content-type="toggleListItem"]:hover) {
		border-left-color: var(--input-border-color-focus);
	}

	/* Nested list indentation - only for deeply nested items */
	.editor :global(.bn-block-group .bn-block-group) {
		margin-left: 1.5em;
		border-left: 1px solid var(--input-border-color);
		padding-left: 1em;
	}

	/* BlockNote quote styling */
	.editor :global(.bn-block-content blockquote) {
		margin: 0.5em 0;
		padding: 0.5em 1em;
		border-left: 4px solid var(--input-border-color-focus);
		background: var(--block-background-fill);
		font-style: italic;
	}

	/* BlockNote code styling */
	.editor :global(.bn-block-content code) {
		background: var(--block-background-fill);
		border: 1px solid var(--input-border-color);
		border-radius: var(--radius-sm);
		padding: 0.1em 0.3em;
		font-family: var(--font-mono);
		font-size: 0.9em;
	}

	.editor :global(.bn-block-content pre) {
		background: var(--block-background-fill);
		border: 1px solid var(--input-border-color);
		border-radius: var(--radius-sm);
		padding: 1em;
		overflow-x: auto;
		margin: 0.5em 0;
	}

	.editor :global(.bn-block-content pre code) {
		background: none;
		border: none;
		padding: 0;
	}

	/* BlockNote link styling */
	.editor :global(.bn-block-content a) {
		color: var(--link-text-color, #0066cc);
		text-decoration: underline;
		cursor: pointer;
		transition: color 0.2s ease;
	}

	.editor :global(.bn-block-content a:hover) {
		color: var(--link-text-color-hover, #004499);
		text-decoration: underline;
	}

	.editor :global(.bn-block-content a:visited) {
		color: var(--link-text-color-visited, #551a8b);
	}

	/* BlockNote image styling */
	.editor :global(.bn-block-content img) {
		max-width: 100%;
		height: auto;
		border-radius: var(--radius-sm);
		border: 1px solid var(--input-border-color);
		box-shadow: var(--shadow-drop);
		margin: 0.5em 0;
		resize: both;
		overflow: auto;
	}

	/* Image block container */
	.editor :global([data-content-type="image"]) {
		text-align: center;
		margin: 1em 0;
	}

	/* File upload drag and drop styling */
	.editor :global(.bn-file-panel) {
		background: var(--background-fill-primary);
		border: 2px dashed var(--input-border-color);
		border-radius: var(--radius-sm);
		padding: 2em;
		text-align: center;
		color: var(--body-text-color-subdued);
		margin: 1em 0;
	}

	.editor :global(.bn-file-panel:hover) {
		border-color: var(--input-border-color-focus);
		background: var(--background-fill-secondary);
	}

	/* Drag over state */
	.editor :global(.bn-file-panel.drag-over) {
		border-color: var(--button-primary-background-fill);
		background: var(--background-fill-secondary);
	}

	/* BlockNote formatting toolbar */
	.editor :global(.bn-formatting-toolbar) {
		background: var(--background-fill-primary);
		border: 1px solid var(--input-border-color);
		border-radius: var(--radius-sm);
		box-shadow: var(--shadow-drop);
	}

	.editor :global(.bn-formatting-toolbar button) {
		background: transparent;
		border: none;
		color: var(--body-text-color);
		padding: 0.5em;
		border-radius: var(--radius-sm);
		cursor: pointer;
	}

	.editor :global(.bn-formatting-toolbar button:hover) {
		background: var(--button-secondary-background-fill-hover);
	}

	.editor :global(.bn-formatting-toolbar button[data-active="true"]) {
		background: var(--button-primary-background-fill);
		color: var(--button-primary-text-color);
	}

	/* Target BlockNote's placeholder styles */
	.editor :global([class*="placeholder-selector"] .bn-block-content[data-is-only-empty-block]::before),
	.editor :global([class*="placeholder-selector"] .bn-block-content[data-is-empty-and-focused]::before),
	.editor :global(.bn-block-content[data-is-only-empty-block]),
	.editor :global(.bn-block-content[data-is-empty-and-focused]) {
		color: var(--body-text-color-subdued, #9ca3af) !important;
		opacity: 0.7 !important;
	}

	/* Disabled state */
	.editor[data-disabled="true"] {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.editor[data-disabled="true"] :global(.bn-editor) {
		pointer-events: none;
	}
</style>
