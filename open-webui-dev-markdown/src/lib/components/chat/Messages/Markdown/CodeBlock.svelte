<script lang="ts">
	import { v4 as uuidv4 } from 'uuid';

	import { getAstNode } from 'svelte-exmarkdown';
	import CodeBlock from '../CodeBlock.svelte';
	const astContext = getAstNode();

	const id = uuidv4();
</script>

<!-- Dump current node -->

{#if $astContext.position.start.line === $astContext.position.end.line}
	<code class="codespan">{$astContext.children[0].value}</code>
{:else}
	<!-- <pre>{JSON.stringify($astContext, null, 2)}</pre> -->
	<CodeBlock {id} lang={$astContext.properties?.class ?? ''} code={$astContext.children[0].value} />
{/if}
