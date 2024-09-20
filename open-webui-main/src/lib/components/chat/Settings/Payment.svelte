<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import ManageModal from './Personalization/ManageModal.svelte';

	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	export let saveSettings: Function;
	let showManageModal = false;

	// Payment Button IDs
	const buttonIds = {
		weekly: "buy_btn_1PuQPuRwKnsYpxFvzlVDEdRL",
		monthly: "buy_btn_1PuQk7RwKnsYpxFvEkt2ku1A",
		yearly: "buy_btn_1PuQkYRwKnsYpxFvXrt7vBQ1"
	};

	const publishableKey = "pk_test_51PpnBARwKnsYpxFvYEybbCzvDIaemssNXcPLAgDY0wMqdgzqbcsUy01mzSt3qpLbVHcopSvko7tkoQtjTKmSyiSd00iGz2zYvS";
</script>

<ManageModal bind:show={showManageModal} />

<form
	class="flex flex-col h-full justify-between space-y-4 text-sm"
	on:submit|preventDefault={() => {
		dispatch('save');
	}}
>
	<div class="flex flex-col space-y-4 items-center">
		<script async src="https://js.stripe.com/v3/buy-button.js"></script>
		<stripe-buy-button
			buy-button-id={buttonIds.weekly}
			publishable-key={publishableKey}
			class="w-full max-w-xs"
		>
		</stripe-buy-button>
		
		<stripe-buy-button
			buy-button-id={buttonIds.monthly}
			publishable-key={publishableKey}
			class="w-full max-w-xs"
		>
		</stripe-buy-button>
		
		<stripe-buy-button
			buy-button-id={buttonIds.yearly}
			publishable-key={publishableKey}
			class="w-full max-w-xs"
		>
		</stripe-buy-button>
	</div>
</form>
