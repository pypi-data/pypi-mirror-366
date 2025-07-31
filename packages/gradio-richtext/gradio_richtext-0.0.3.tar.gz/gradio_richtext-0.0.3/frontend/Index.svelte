<svelte:options accessors={true} />

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { BlockTitle } from "@gradio/atoms";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { onMount, onDestroy } from "svelte";
	import { Editor } from "@tiptap/core";
	import StarterKit from "@tiptap/starter-kit";
	import Image from "@tiptap/extension-image";
	import Link from "@tiptap/extension-link";
	import FileHandler from "@tiptap/extension-file-handler";


	export let gradio: Gradio<{
		change: never;
		input: never;
		clear_status: LoadingStatus;
	}>;
	export let label = "Textbox";
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
	let editor: Editor;

	// Custom markdown serializer that works in the browser
	function renderToMarkdown(content: any): string {
		function serializeNode(node: any, isTopLevel = false): string {
			switch (node.type) {
				case 'doc':
					const blocks = node.content?.map((child: any) => serializeNode(child, true)).filter((text: string) => text.trim()) || [];
					return blocks.join('\n\n');
				
				case 'paragraph':
					const paragraphText = node.content?.map((child: any) => serializeNode(child)).join('') || '';
					return paragraphText;
				
				case 'heading':
					const level = node.attrs?.level || 1;
					const headingText = node.content?.map((child: any) => serializeNode(child)).join('') || '';
					return '#'.repeat(level) + ' ' + headingText;
				
				case 'bulletList':
					const bulletItems = node.content?.map((item: any) => {
						const itemText = serializeNode(item);
						return '- ' + itemText;
					}).join('\n') || '';
					return bulletItems;
				
				case 'orderedList':
					const orderedItems = node.content?.map((item: any, index: number) => {
						const itemText = serializeNode(item);
						return `${index + 1}. ` + itemText;
					}).join('\n') || '';
					return orderedItems;
				
				case 'listItem':
					return node.content?.map((child: any) => serializeNode(child)).join('') || '';
				
				case 'text':
					let textContent = node.text || '';
					if (node.marks) {
						for (const mark of node.marks) {
							switch (mark.type) {
								case 'bold':
									textContent = `**${textContent}**`;
									break;
								case 'italic':
									textContent = `*${textContent}*`;
									break;
								case 'link':
									textContent = `[${textContent}](${mark.attrs?.href || ''})`;
									break;
								case 'code':
									textContent = `\`${textContent}\``;
									break;
							}
						}
					}
					return textContent;
				
				case 'image':
					const src = node.attrs?.src || '';
					const alt = node.attrs?.alt || '';
					return `![${alt}](${src})`;
				
				case 'hardBreak':
					return '\n';
				
				case 'codeBlock':
					const code = node.content?.map((child: any) => serializeNode(child)).join('') || '';
					return '```\n' + code + '\n```';
				
				default:
					return node.content?.map((child: any) => serializeNode(child)).join('') || '';
			}
		}
		
		return serializeNode(content);
	}

	// Function to improve markdown formatting with proper newlines
	function cleanMarkdown(markdown: string): string {
		return markdown
			// Ensure double newlines between different block elements
			.replace(/(\n)([-*+]|\d+\.)/g, '\n\n$2')
			// Ensure lists end with double newline
			.replace(/([-*+]|\d+\.)[^\n]*\n(?![-*+]|\d+\.|\s*$)/g, (match) => {
				return match.trimEnd() + '\n\n';
			})
			// Clean up multiple consecutive newlines (more than 2)
			.replace(/\n{3,}/g, '\n\n')
			// Ensure content ends with single newline
			.replace(/\n*$/, '\n');
	}

	const extensions = [
		StarterKit.configure({
			bulletList: {
				keepMarks: true,
				keepAttributes: false,
			},
			orderedList: {
				keepMarks: true,
				keepAttributes: false,
			},
			codeBlock: false,
			link: false,
			hardBreak: {
				keepMarks: false,
			},
			paragraph: {
				HTMLAttributes: {},
			}
		}),
		Image.extend({
			renderHTML({ HTMLAttributes }) {
				return [
					'div',
					{ class: 'resizable-image-container' },
					['img', HTMLAttributes]
				];
			},
		}).configure({ 
			allowBase64: true,
		}),
		FileHandler.configure({
			allowedMimeTypes: ['image/*'],
			onPaste: (editor, files) => {
				files.forEach(file => {
					if (file.type.startsWith('image/')) {
						const reader = new FileReader();
						reader.onload = () => 
							editor.commands.setImage({ src: reader.result as string, alt: file.name });
						reader.readAsDataURL(file);
					}
				});
			}
		}),
		Link.configure({ 
			openOnClick: false,
			defaultProtocol: 'https',
		}).extend({
			addKeyboardShortcuts() {
				return {
					"Mod-k": () => {
						const input = prompt("Enter URL") ?? "";
						if (input) {
							const href = input.match(/^https?:\/\//) ? input : `https://${input}`;
							this.editor.chain().focus().setLink({ href }).setTextSelection(this.editor.state.selection.to).unsetMark('link').run();
						} else {
							this.editor.commands.unsetLink();
						}
						return true;
					},
				};
			},
		}),
	];

	onMount(() => {
		editor = new Editor({
			element,
			extensions,
			content: value,
			editable: interactive,

			onUpdate: ({ editor }) => {
				const rawMarkdown = renderToMarkdown(editor.getJSON());
				value = cleanMarkdown(rawMarkdown);
				gradio.dispatch("change");
				if (!value_is_output) {
					gradio.dispatch("input");
				}
			},
		});

		// Handle drag and drop manually
		if (element) {
			element.addEventListener('dragover', (e) => {
				e.preventDefault();
				e.stopPropagation();
			});
			
			element.addEventListener('drop', (e) => {
				const dragEvent = e as DragEvent;
				e.preventDefault();
				e.stopPropagation();
				
				const files = Array.from(dragEvent.dataTransfer?.files || []);
				if (files.length > 0) {
					files.forEach(file => {
						if (file.type.startsWith('image/')) {
							const reader = new FileReader();
							reader.onload = (event) => {
								const src = event.target?.result as string;
								editor.commands.setImage({ src, alt: file.name });
							};
							reader.readAsDataURL(file);
						}
					});
				}
			});
		}

	});

	onDestroy(() => {
		if (editor) {
			editor.destroy();
		}
	});

	$: if (editor && value !== cleanMarkdown(renderToMarkdown(editor.getJSON()))) {
		editor.commands.setContent(value);
	}

	$: if (value === null) value = "";

	$: if (editor) {
		editor.setEditable(interactive);
	}
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
			class="editor scroll-hide"
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
	}

	.editor :global(.ProseMirror) {
		outline: none !important;
		box-shadow: var(--input-shadow);
		background: var(--input-background-fill);
		padding: var(--input-padding);
		color: var(--body-text-color);
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		min-height: 1em;
	}

	.container > .editor :global(.ProseMirror) {
		border: var(--input-border-width) solid var(--input-border-color);
		border-radius: var(--input-radius);
	}

	.editor :global(.ProseMirror[contenteditable="false"]) {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.editor :global(.ProseMirror:focus) {
		box-shadow: var(--input-shadow-focus);
		border-color: var(--input-border-color-focus);
	}
	.editor :global(.ProseMirror ul),
	.editor :global(.ProseMirror ol) {
		padding-left: 1.5em;
		margin: 0.5em 0;
	}

	.editor :global(.ProseMirror li) {
		margin: 0.2em 0;
	}

	.editor :global(.ProseMirror p) {
		margin: 0.5em 0;
	}

	.editor :global(.ProseMirror p:first-child) {
		margin-top: 0;
	}

	.editor :global(.ProseMirror p:last-child) {
		margin-bottom: 0;
	}

	/* Resizable image container */
	.editor :global(.ProseMirror .resizable-image-container) {
		resize: both;
		overflow: auto;
		max-width: 100%;
		border: 2px solid var(--input-border-color);
		border-radius: var(--radius-sm);
		margin: 0.25em;
		display: inline-block;
		cursor: nw-resize;
		vertical-align: middle;
	}

	.editor :global(.ProseMirror .resizable-image-container:hover) {
		border-color: var(--input-border-color-focus);
	}

	.editor :global(.ProseMirror .resizable-image-container img) {
		width: 100%;
		height: 100%;
		object-fit: contain;
		display: block;
		cursor: pointer;
	}

	.editor :global(.ProseMirror a) {
		color: var(--link-text-color, #2563eb);
		text-decoration: underline;
		cursor: pointer;
	}

	.editor :global(.ProseMirror a:hover) {
		color: var(--link-text-color-hover, #1d4ed8);
		text-decoration: underline;
	}
</style>
