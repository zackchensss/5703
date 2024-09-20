<script lang="ts">
	import { getContext, tick } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { models, settings, user } from '$lib/stores';
	import { updateUserSettings } from '$lib/apis/users';
	import { getModels as _getModels } from '$lib/apis';
	import { goto } from '$app/navigation';

	import Modal from '../common/Modal.svelte';
	import Account from './Settings/Account.svelte';
	import About from './Settings/About.svelte';
	import General from './Settings/General.svelte';
	import Interface from './Settings/Interface.svelte';
	import Audio from './Settings/Audio.svelte';
	import Chats from './Settings/Chats.svelte';
	import User from '../icons/User.svelte';
	import Personalization from './Settings/Personalization.svelte';
	import Payment from './Settings/Payment.svelte';
	import Plan from './Settings/Plan.svelte';


	const i18n = getContext('i18n');

	export let show = false;

	const saveSettings = async (updated) => {
		console.log(updated);
		await settings.set({ ...$settings, ...updated });
		await models.set(await getModels());
		await updateUserSettings(localStorage.token, { ui: $settings });
	};

	const getModels = async () => {
		return await _getModels(localStorage.token);
	};

	let selectedTab = 'general';

	// Function to handle sideways scrolling
	const scrollHandler = (event) => {
		const settingsTabsContainer = document.getElementById('settings-tabs-container');
		if (settingsTabsContainer) {
			event.preventDefault(); // Prevent default vertical scrolling
			settingsTabsContainer.scrollLeft += event.deltaY; // Scroll sideways
		}
	};

	const addScrollListener = async () => {
		await tick();
		const settingsTabsContainer = document.getElementById('settings-tabs-container');
		if (settingsTabsContainer) {
			settingsTabsContainer.addEventListener('wheel', scrollHandler);
		}
	};

	const removeScrollListener = async () => {
		await tick();
		const settingsTabsContainer = document.getElementById('settings-tabs-container');
		if (settingsTabsContainer) {
			settingsTabsContainer.removeEventListener('wheel', scrollHandler);
		}
	};

	$: if (show) {
		addScrollListener();
	} else {
		removeScrollListener();
	}
</script>

<Modal bind:show>
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-1">
			<div class=" text-lg font-medium self-center">{$i18n.t('Subscriptions')}</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
					/>
				</svg>
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full p-4 md:space-x-4">
			<div
				id="settings-tabs-container"
				class="tabs flex flex-row overflow-x-auto space-x-1 md:space-x-0 md:space-y-1 md:flex-col flex-1 md:flex-none md:w-40 dark:text-gray-200 text-xs text-left mb-3 md:mb-0"
			>
				

				<button
					class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 md:flex-none flex text-right transition {selectedTab ===
					'payment'
						? 'bg-gray-200 dark:bg-gray-800'
						: ' hover:bg-gray-100 dark:hover:bg-gray-850'}"
					on:click={() => {
						selectedTab = 'payment';
					}}
				>
					<div class=" self-center mr-2">
						<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						class="w-4 h-4"
						>
						<path
							fill-rule="evenodd"
							d="M2 3.5A2.5 2.5 0 0 1 4.5 1h7A2.5 2.5 0 0 1 14 3.5v9A2.5 2.5 0 0 1 11.5 15h-7A2.5 2.5 0 0 1 2 12.5v-9Zm2 .5a.5.5 0 0 0-.5.5v6a.5.5 0 0 0 .5.5h8a.5.5 0 0 0 .5-.5v-6a.5.5 0 0 0-.5-.5h-8Zm0 2h8v1h-8v-1Z"
							clip-rule="evenodd"
						/>
						</svg>
					</div>
					<div class=" self-center">{$i18n.t('Payment')}</div>
				</button>

				<button
					class="px-2.5 py-2.5 min-w-fit rounded-lg flex-1 md:flex-none flex text-right transition {selectedTab ===
					'plan'
						? 'bg-gray-200 dark:bg-gray-800'
						: ' hover:bg-gray-100 dark:hover:bg-gray-850'}"
					on:click={() => {
						selectedTab = 'plan';
					}}
				>
					<div class=" self-center mr-2">
						<User />
					</div>
					<div class=" self-center">{$i18n.t('Your Plan')}</div>
				</button>

				
			</div>
			<div class="flex-1 md:min-h-[28rem]">
				{#if selectedTab === 'general'}
					<General
						{getModels}
						{saveSettings}
						on:save={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
				{:else if selectedTab === 'interface'}
					<Interface
						{saveSettings}
						on:save={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
					{:else if selectedTab === 'payment'}
					<Payment
						{saveSettings}
						on:save={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
				{:else if selectedTab === 'personalization'}
					<Personalization
						{saveSettings}
						on:save={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
				{:else if selectedTab === 'plan'}
					<Plan
						{saveSettings}
						on:save={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
				{:else if selectedTab === 'audio'}
					<Audio
						{saveSettings}
						on:save={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
				{:else if selectedTab === 'chats'}
					<Chats {saveSettings} />
				{:else if selectedTab === 'account'}
					<Account
						saveHandler={() => {
							toast.success($i18n.t('Settings saved successfully!'));
						}}
					/>
				{:else if selectedTab === 'about'}
					<About />
				{/if}
			</div>
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>
