<script lang="ts">
	import Image from '$lib/components/common/Image.svelte';
	import { getAstNode } from 'svelte-exmarkdown';
	const astContext = getAstNode();
</script>

<Image src={$astContext.properties.src} alt={$astContext.properties.alt} />
