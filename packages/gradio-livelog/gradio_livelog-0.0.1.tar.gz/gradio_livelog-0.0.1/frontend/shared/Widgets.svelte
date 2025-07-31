<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import Copy from "./Copy.svelte";
	import Download from "./Download.svelte";
	import Clear from "./Clear.svelte"; 
	import { IconButtonWrapper } from "@gradio/atoms";
	export let value: string;
	const dispatch = createEventDispatcher();

</script>

<IconButtonWrapper>
	<Clear on:click={() => dispatch('clear')} />
	<Copy {value} />
	<Download {value} />
</IconButtonWrapper>
