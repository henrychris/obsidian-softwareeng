# State and Effects
```html
<script>
  let elapsed = $state(0);
  let interval = $state(1000);
  
  $effect(() => {
    const timer = setInterval(() => {
      elapsed += 1;
    }, interval);
    
    // Cleanup function to clear the interval when dependencies change
    return () => clearInterval(timer);
  });
</script>

<button onclick={() => interval /= 2}>speed up</button>
<button onclick={() => interval *= 2}>slow down</button>
<p>elapsed: {elapsed}</p>
```

Here, we declare two reactive variables: `elapsed` and `interval`. The  `$effect` block is a piece of code that re-runs each time its dependencies are updated. 
In this code snippet, when `speed up` is clicked, the interval is divided in half and a new timer is set to update `elapsed`. The old timer is deleted as well. 
When `slow down` is clicked the inverse happens.

In a nutshell, `$effect` watches for changes to its dependencies and runs the code within it. The function it returns is used for cleanup the next time the effect runs. First the cleanup runs, then the `$effect` code follows suit.

# Each
When working with lists of data, we might want to render multiple items in the same component.
```html
<script>
	const colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'];
	let selected = $state(colors[0]);
</script>

<div>
{#each colors as color, i}
		<button
		style="background: {color}"
		aria-label="{color}"
		aria-current={selected === color}
		onclick={() => selected = color}
	>{i + 1}</button>
{/each}
</div>
```