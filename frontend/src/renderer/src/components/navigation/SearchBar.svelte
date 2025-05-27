<script lang="ts">
  import axios from 'axios'
  import { push } from 'svelte-spa-router';
  import { searchResults } from '../stores/search';
  const baseUrl = 'http://localhost:8000/api'
  // svelte-ignore non_reactive_update
  let searchQuery = ''
  const searchYoutube = async () => {
    try {
      const response = await axios.get(`${baseUrl}/search`, {
        params: {
          q: searchQuery
        }
      })
      searchResults.set(response?.data)
      console.log(searchResults)
      push('/search');
    } catch (error) {
      console.error(error)
    }
  }
</script>

<div class="w-full bg-gray-900 text-white shadow-md px-4 py-3 flex items-center justify-center">
  <input
    type="search"
    placeholder="Search for music"
    bind:value={searchQuery}
    class="p-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
  />
  <button
    onclick={searchYoutube}
    class="ml-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium cursor-pointer transition"
    >Search</button
  >
</div>
