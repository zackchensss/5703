<script lang="ts">
	import type { Plugin } from 'svelte-exmarkdown';
	import Markdown from 'svelte-exmarkdown';
	import CodeBlock from './Markdown/CodeBlock.svelte';
	import Image from './Markdown/Image.svelte';

	export let content = '# Hello World';
	const plugins: Plugin[] = [{ renderer: {} }];
</script>

<div class="">
	<Markdown md={content} {plugins} />
</div>
