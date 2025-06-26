<script lang="ts">
  import axios from 'axios'
  import { push } from 'svelte-spa-router'
  import { baseUrl, searchResults } from '../stores/Variables'
  import logo from '../../assets/icon.png'
  
  let clicked: boolean = false
  let searchQuery = ''

  const searchYoutube = async () => {
    if (clicked) return
    clicked = true
    try {
      const response = await axios.get(`${baseUrl}/search`, {
        params: {
          q: searchQuery,
          max_results: 25
        }
      })
      searchResults.set(response?.data)
      push('/search')
    } catch (error) {
      console.error(error)
    } finally {
      clicked = false
    }
  }
</script>

<div class="w-full bg-gray-900 text-white shadow-md px-6 py-3 flex flex-wrap items-center justify-between gap-4">
  <!-- Left: Logo -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="flex items-center flex-shrink-0 cursor-pointer" onclick={() => push('/')}>
    <img src={logo} alt="logo" class="h-12 w-auto" />
  </div>

  <!-- Center: Search bar -->
  <div class="flex flex-1 max-w-2xl min-w-[280px]">
    <input
      type="search"
      placeholder="Search for music"
      bind:value={searchQuery}
      onkeydown={(e) => { if (e.key === 'Enter') searchYoutube() }}
      class="flex-grow p-3 rounded-l-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 transition"
    />
    <button
      onclick={searchYoutube}
      class="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-r-lg font-semibold text-white transition cursor-pointer"
      aria-label="Search"
      disabled={clicked}
    >
      {clicked ? 'Searching...' : 'Search'}
    </button>
  </div>

  <!-- Right: Download button -->
  <button
    onclick={() => push('/download')}
    class="px-5 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold text-white transition flex-shrink-0 cursor-pointer"
  >
    Download
  </button>
</div>
