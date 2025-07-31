<script context="module" lang="ts">
	export { default as BaseButton } from "./shared/DataFrameDownload.svelte";
</script>

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { type FileData } from "@gradio/client";

	import DataFrameDownload from "./shared/DataFrameDownload.svelte";

	export let elem_id: string = "";
	export let elem_classes: string[] = [];
	export let visible: boolean = true;
	export let variant: "primary" | "secondary" | "stop" = "secondary";
	export let interactive: boolean;
	export let size: "sm" | "md" | "lg" = "lg";
	export let scale: number | null = null;
	export let icon: FileData | null = null;
	export let min_width: number | undefined = undefined;
	export let label: string | null;

	// props passed from the `gradio` Python backend
	export let gradio: Gradio<{click: never;}>;

	// `value` will receive the JSON string from `DataFrameDownload.postprocess`
	export let value: string | null = null;
</script>

<DataFrameDownload
	{value}
	{variant}
	{elem_id}
	{elem_classes}
	{size}
	{scale}
	{icon}
	{min_width}
	{visible}
	{label}
	disabled={!value || !interactive}
	on:click={() => gradio.dispatch("click")}
/>

<style>

</style>