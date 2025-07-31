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

	onMount(() => {
		editor = new Editor({
			element,
			extensions: [
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
					hardBreak: {
						keepMarks: false,
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
					inline: true,
					allowBase64: true,
				}),
				FileHandler.configure({
					accept: ['image/*', 'application/pdf'],
					onDrop(editor: Editor, files: File[]) {
						files.forEach(file => {
							const reader = new FileReader();
							reader.onload = () => 
								editor.commands.setImage({ src: reader.result as string, alt: file.name });
							reader.readAsDataURL(file);
						});
						return true;
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
			],
			content: value,
			editable: interactive,
			onUpdate: ({ editor }) => {
				value = editor.getHTML();
				gradio.dispatch("change");
				if (!value_is_output) {
					gradio.dispatch("input");
				}
			},
		});

	});

	onDestroy(() => {
		if (editor) {
			editor.destroy();
		}
	});

	$: if (editor && value !== editor.getHTML()) {
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
		width: 300px;
		height: 200px;
		min-width: 100px;
		min-height: 80px;
		max-width: 100%;
		border: 2px solid var(--input-border-color);
		border-radius: var(--radius-sm);
		margin: 0.5em 0;
		display: inline-block;
		cursor: nw-resize;
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
