<script lang="ts">
    import { getCurrentSubscription, getSubscriptionHistory } from '$lib/apis/subscriptions';
    import { toast } from 'svelte-sonner';
    import { createEventDispatcher, onMount, getContext } from 'svelte';
    import ManageModal from './Personalization/ManageModal.svelte';

    // 定义接口类型
    interface Subscription {
        plan: string;
        status?: string;
        startDate: string;
        endDate: string;
    }

    // 用户门户链接
    const portalLink = "https://billing.stripe.com/p/login/test_bIYdRy2q67c65LWdQQ?prefilled_email=";
    let userEmail = "user@example.com";

    const dispatch = createEventDispatcher();
    const i18n = getContext('i18n');
    export let saveSettings: Function;
    let showManageModal = false;

    // Initialization variable
    let currentSubscription: Subscription | null = null;
    let subscriptionHistory: Subscription[] = [];

    // The API is called when the component is mounted
    onMount(async () => {
        try {
            // Get current subscription information
            currentSubscription = await getCurrentSubscription();
            // Get subscription history
            subscriptionHistory = await getSubscriptionHistory();
        } catch (error) {
            console.error('Error fetching subscription data:', error);
            toast.error('Failed to load subscription data.');
        }
    });

    // Handle click for login portal
    function redirectToPortal() {
        window.location.href = `${portalLink}${userEmail}`;
    }
</script>

<ManageModal bind:show={showManageModal} />

<form
    class="flex flex-col h-full justify-between space-y-3 text-sm"
    on:submit|preventDefault={() => {
        dispatch('save');
    }}
>
    <!-- 使用绑定的动态数据 -->
    <div class="flex h-full space-x-6">
        <!-- Left Sidebar with Subscription and Information -->
        <div class="w-1/3">
            <!-- Current Subscription Section -->
            <div class="mb-6">
                <h2 class="text-lg font-bold">Subscription</h2>
                {#if currentSubscription}
                    <div class="p-6 bg-gray-100 rounded-lg min-w-[400px]">
                        <p><strong>Plan:</strong> {currentSubscription.plan}</p>
                        <p><strong>Status:</strong> {currentSubscription.status}</p>
                        <p><strong>Start Date:</strong> {currentSubscription.startDate}</p>
                        <p><strong>End Date:</strong> {currentSubscription.endDate}</p>
                    </div>
                {:else}
                    <p>No current subscription found.</p>
                {/if}
            </div>

            <!-- Subscription History Section -->
            <div>
                <h2 class="text-lg font-bold">Information</h2>
                {#if subscriptionHistory.length > 0}
                    <ul class="space-y-3">
                        {#each subscriptionHistory as record}
                            <li class="p-6 bg-gray-50 rounded-lg min-w-[400px]">
                                <p style="display: block; margin-bottom: 0.5rem;"><strong>Plan:</strong> {record.plan}</p>
                                <p style="display: block; margin-bottom: 0.5rem;"><strong>Start Date:</strong> {record.startDate}</p>
                                <p style="display: block; margin-bottom: 0.5rem;"><strong>End Date:</strong> {record.endDate}</p>
                            </li>
                        {/each}
                    </ul>
                {:else}
                    <p>No subscription history available.</p>
                {/if}
            </div>

            <!-- User Portal Section -->
            <div>
                <button class="bottom-4 right-4 px-4 py-2 bg-blue-500 text-white rounded-lg" style="margin: 20px 0px 10px; width:150px" on:click={redirectToPortal}>
                    Go to User Portal
                </button>
            </div>
        </div>

        <!-- Right Content Area (if needed) -->
        <div class="w-2/3">
            <!-- Additional content or features can be added here -->
        </div>
    </div>

    <style>
        h2 {
            margin-bottom: 0rem;
            color: #333;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 1.5rem;
            font-size: 0.85rem;
        }
        li p {
            margin: 0rem 0;
        }
        button {
            cursor: pointer;
        }
    </style>
</form>
