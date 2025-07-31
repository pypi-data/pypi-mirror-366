<!-- frontend/src/shared/LiveLogPanel.svelte -->

<script lang="ts">
	import { afterUpdate, createEventDispatcher } from "svelte";
	import Widgets from "./Widgets.svelte";

	// -------------------------------------------------------------------------
	// Props received from the Gradio backend via index.svelte
	// -------------------------------------------------------------------------

	/** The incoming value from the Gradio backend. Can be null, an array, or a single object. */
	export let value: Record<string, any> | Array<Record<string, any>> | null = null;
	/** The height of the component. */
	export let height: number | string;
	/** Whether to automatically scroll to the latest log entry. */
	export let autoscroll: boolean;
	/** Whether to display line numbers next to log entries. */
	export let line_numbers: boolean;
	/** The background color of the log display area. */
	export let background_color: string;
	/** The current display mode: "full", "log", or "progress". */
	export let display_mode: "full" | "log" | "progress";
	
	const dispatch = createEventDispatcher();
	let log_container: HTMLElement;

	// -------------------------------------------------------------------------
	// Internal component state
	// -------------------------------------------------------------------------

	/** Internal object that holds the current state of the progress bar. */
    let progress = { visible: false, current: 0, total: 100, desc: "", percentage: 0, rate: 0.0, status: "running" };
	/** Internal array that accumulates all received log lines. */
	let log_lines: { level: string; content: string }[] = [];
	/** A plain text representation of all logs for the copy/download buttons. */
	let all_logs_as_text = "";
	/** A reactive variable to control the component's height based on display mode. */
    let height_style: string;

	// -------------------------------------------------------------------------
	// Reactive Logic
	// -------------------------------------------------------------------------

    // Dynamically adjust the component's height style.
    $: {
        if (display_mode === 'progress' && progress.visible) {
            height_style = 'auto'; // Shrink to fit only the progress bar content.
        } else {
            height_style = typeof height === 'number' ? height + 'px' : height;
        }
    }

	// This is the core reactive block that processes incoming `value` updates from Gradio.
	$: {
		if (value === null) {
			// A `null` value is the signal to clear the component's state.
			log_lines = [];
			progress = { visible: false, current: 0, total: 100, desc: "", percentage: 0, rate: 0.0, status: "running" };
			all_logs_as_text = "";
		} else if (value) {
			if (Array.isArray(value)) {
				// This handles an initial state load if the backend provides a full list.
			} else if (typeof value === 'object' && value.type) {
				// This is the primary streaming case: handles a single new data object.
				if (value.type === "log") {
					log_lines = [...log_lines, { level: value.level || 'INFO', content: value.content }];
				} else if (value.type === "progress") {
					progress.visible = true;
					progress.current = value.current;
					progress.total = value.total || 100;
					progress.desc = value.desc;
					progress.rate = value.rate || 0.0;
					progress.percentage = progress.total > 0 ? ((value.current / progress.total) * 100) : 0;
					progress.status = value.status || "running";
				}
			}
			// Update the plain text version of logs after every change.
			all_logs_as_text = log_lines.map(l => l.content).join('\n');
		}
	}

	// This lifecycle function runs after the DOM has been updated.
	afterUpdate(() => {
		if (autoscroll && log_container) {
			// Scroll the log container to the bottom to show the latest entry.
			log_container.scrollTop = log_container.scrollHeight;
		}
	});
</script>

<div class="panel-container" style:height={height_style}>
	<!-- Conditionally render the log view based on the display_mode prop. -->
	<div class="log-view-container" style:display={display_mode === 'progress' ? 'none' : 'flex'}>
		<div class="header">
			<Widgets bind:value={all_logs_as_text} on:clear={() => dispatch('clear')} />
		</div>
		<div class="log-panel" bind:this={log_container} style="background-color: {background_color};">
			{#each log_lines as log, i}
				<div class="log-line">
					{#if line_numbers}<span class="line-number">{i + 1}</span>{/if}
					<pre class="log-content log-level-{log.level.toLowerCase()}">{log.content}</pre>
				</div>
			{/each}
		</div>
	</div>

	<!-- Conditionally render the progress bar view. -->
	{#if progress.visible && (display_mode === 'full' || display_mode === 'progress')}
		<div class="progress-container">
			<div class="progress-label-top">
				<span>{progress.desc}</span>
				<span>{progress.rate.toFixed(1)} it/s</span> 
			</div>
			<div class="progress-bar-background">
				<!-- Conditionally apply CSS classes based on the progress status. -->
				<div 
					class="progress-bar-fill" 
					class:success={progress.status === 'success'}
					class:error={progress.status === 'error'}
					style="width: {progress.percentage.toFixed(1)}%;"
				></div>
			</div>
			<div class="progress-label-bottom">
				<span>{Math.round(progress.percentage)}%</span>
				<span>{progress.current} / {progress.total}</span>
			</div>
		</div>
	{/if}
</div>

<style>
	.panel-container {
		display: flex;
		flex-direction: column;
		border: 1px solid var(--border-color-primary);
		border-radius: 0 !important;
		background-color: var(--background-fill-primary);
		overflow: hidden;
	}
	
    .log-view-container {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        min-height: 0; /* Ensures proper flexbox behavior in a column. */
    }
	.header {		
		border-bottom: 1px solid var(--border-color-primary);
		background-color: var(--background-fill-secondary);
		display: flex;
		justify-content: flex-end;
        flex-shrink: 0; /* Prevents the header from shrinking. */
	}
	.log-panel {
		flex-grow: 1;
		font-family: var(--font-mono, monospace);
		font-size: var(--text-sm);
		overflow-y: auto;
		/* padding: var(--spacing-md); */
		color: #f8f8f8;
	}
	.log-line { 
		display: flex; 
	}
	.line-number { 
		opacity: 0.6; 
		padding-right: var(--spacing-lg); 
		user-select: none; 
		text-align: right; 
		min-width: 3ch; 
	}
	.log-content { 
		margin: 0; 
		white-space: pre-wrap; 
		word-break: break-word; 
	}
	
	/* Styles for different log levels */
	.log-level-info { color: inherit; }
	.log-level-debug { color: #888888; }
	.log-level-warning { color: #facc15; }
	.log-level-error { color: #ef4444; }
	.log-level-critical { 
		background-color: #ef4444; 
		color: white; 
		font-weight: bold; 
		padding: 0 0.25rem;
	}
	.log-level-success { color: #22c55e; }
	
	.progress-container { 
		padding: var(--spacing-sm) var(--spacing-md); 
		border-top: 1px solid var(--border-color-primary); 
		background: var(--background-fill-secondary);
	}
	.progress-label-top, .progress-label-bottom {
		display: flex;
		justify-content: space-between;
		font-size: var(--text-sm);
		color: var(--body-text-color-subdued);
	}
	.progress-label-top {
		margin-bottom: var(--spacing-xs);
	}
	.progress-label-bottom {
		margin-top: var(--spacing-xs);
	}
	.progress-bar-background { 
		width: 100%; 
		height: 8px; 
		background-color: var(--background-fill-primary); 
		border-radius: var(--radius-full); 
		overflow: hidden; 
	}
	.progress-bar-fill { 
		height: 100%; 
		background-color: var(--color-accent); /* Default "running" color */
		border-radius: var(--radius-full); 
		transition: width 0.1s linear, background-color 0.3s ease;
	}

	/* Styles for different progress bar statuses */
	.progress-bar-fill.success {
		background-color: var(--color-success, #22c55e);
	}
	.progress-bar-fill.error {
		background-color: var(--color-error, #ef4444);
	}
</style>