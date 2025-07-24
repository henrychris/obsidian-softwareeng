Using `setContext`, we can add a value to context, which will be available to all children of the parent component. Technically, we can add a value to context in the layout.svelte, and it would be available to all the components in the application.

Note that values set in context are not reactive by default. We can get around this by setting proxied objects in context instead. See: [Deep State](https://svelte.dev/docs/svelte/$state#Deep-state)

```ts
let count = $state(5);
setContext("key", 5) // not reactive. value would not change in child component
```

But if we use deeply reactive classes, they will maintain reactivity. 
```ts
class Count {
	current = $state(5);
}

const count = new Count();
setContext("key", count);
```

Here's how we can use the context API with a class:
```ts
import type { Toast } from '$lib/types';
import { getContext, setContext } from 'svelte';

export class ToastManager {
	toasts = $state<Toast[]>([]);

	addToast(toast: Toast) {
		this.toasts.push(toast);
	}

	removeToast(toastId: string) {
		this.toasts = this.toasts.filter((toast) => toast.id !== toastId);
	}
}

const TOAST_CTX = 'TOAST_CTX';

export function setToastState(): ToastManager {
	const toastState = new ToastManager();
	setContext(TOAST_CTX, toastState);
	return toastState;
}

export function getToastState(): ToastManager {
	return getContext<ToastManager>(TOAST_CTX);
}
```

We can set the context state in layout.svelte like this:

```ts
// layout.svelte

<script lang="ts">
	import { setToastState } from '$lib/stores/toast.svelte';
	
	setToastState();
</script>
```

References:
- [Global Stores Are Dangerous](https://www.youtube.com/watch?v=EyDV5XLfagg)
- [Context + Classes](https://www.youtube.com/watch?v=e1vlC31Sh34)
- [Svelte Context API](https://svelte.dev/docs/svelte/context)