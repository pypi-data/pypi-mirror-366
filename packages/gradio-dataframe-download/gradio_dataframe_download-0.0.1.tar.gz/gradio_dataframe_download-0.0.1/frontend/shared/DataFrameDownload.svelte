<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { type FileData } from "@gradio/client";
  import { BaseButton } from "@gradio/button";

	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let variant: "primary" | "secondary" | "stop" = "secondary";
	export let size: "sm" | "md" | "lg" = "lg";
	export let value: string | null = null;
	export let icon: FileData | null = null;
	export let disabled = false;
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let label: string | null ="";
	const dispatch = createEventDispatcher();

  /**
	 * Button `click` callback function.
	 *
	 * This function handles the entire client-side download process, by
	 * parsing JSON into CSV and then creating a `Blob` (Binary Large Object),
	 * which is a file-like object of immutable, raw data. The MIME type is set
	 * to text/csv;charset=utf-8;.
	 * 
	 * Calling `URL.createObjectURL(blob)` creates a unique, temporary URL that
	 * points directly to the `Blob` object residing in memory. This URL is only
	 * valid within the context of the current document.
	 *
	 * @since      0.0.1
	 * @access     private
	 * 
	 * @listens event:click
	 *
	 * @param {string | null} csv_data - The CSV data as a JSON string.
	 * @returns {Promise<void>}
	 */
	function downloadCSVData(csv_data: string | null): void {
		dispatch("click")
		if (!csv_data) {
			console.warn("`DataFrameDownloadButton` was not sent any data");
			return;
		}

		try {
			// 1: parse the JSON string received from the backend
			const parsedData = JSON.parse(csv_data);
			if (
				!parsedData ||
				// expecting `columns` & `data` keys
				!Array.isArray(parsedData.columns) ||
				!Array.isArray(parsedData.data)
			) {
				throw new Error("Invalid data format received from backend");
			}

			// 2: construct CSV content from the parsed data
			const columns = parsedData.columns;
			const data = parsedData.data;

			// create the header row.
			const header = columns.join(',');

			// Create the data rows, ensuring proper handling of commas within data.
			const rows = data.map((row: any) =>
				// convert values to strings
				row.map(String) 
					// quote fields and escape double quotes
					.map((val: string) => `"${val.replace(/"/g, '""')}"`) 
				  .join(',')
			);

			// combine header & rows. Prepend UTF-8 BOM for Excel compatibility
			const csvContent = '\uFEFF' + [header,...rows].join('\n');

			// 3: trigger client-side download using a `Blob`
			// https://developer.mozilla.org/en-US/docs/Web/API/Blob
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const url = URL.createObjectURL(blob);
			const link = document.createElement('a');

			// generate a descriptive filename
			const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
			const filename = `dataframe_${timestamp}.csv`;

			link.setAttribute('href', url);
			link.setAttribute('download', filename);
			link.style.visibility = 'hidden';
			document.body.appendChild(link);

			// programmatically click the link to start the download
			link.click();

			// clean up by removing the link and revoking the object URL to free up memory
			document.body.removeChild(link);
			URL.revokeObjectURL(url);

		} catch (e) {
			// TODO: add UI indicator explaining the error
			console.error("Failed to generate/download CSV:", e);
		}
	}
</script>

<BaseButton
	{size}
	{variant}
	{elem_id}
	{elem_classes}
	{visible}
	on:click={() => {downloadCSVData(value);}}
	{scale}
	{min_width}
	{disabled}
>
	{#if icon}
		<img class="button-icon" src={icon.url} alt={`${label} icon`} />
	{:else}
		{label}
	{/if}
</BaseButton>

<style>
	.button-icon {
		width: var(--text-xl);
		height: var(--text-xl);
		margin-right: var(--spacing-xl);
	}
</style>