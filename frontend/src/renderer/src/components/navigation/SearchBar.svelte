<script lang="ts">
  // Import necessary dependencies
  import axios from 'axios'
  import { push } from 'svelte-spa-router'
  import { baseUrl, searchResults } from '../stores/Variables'

  // State to prevent multiple simultaneous search requests
  let clicked: boolean = false

  // Search query input value
  let searchQuery = ''

  // Handle search functionality
  const searchYoutube = async () => {
    try {
      // Prevent multiple simultaneous requests
      if (clicked) return
      clicked = true

      // Make API request to search endpoint with query parameter
      const response = await axios.get(`${baseUrl}/search`, {
        params: {
          q: searchQuery
        }
      })

      // Store search results in global store
      searchResults.set(response?.data)
      console.log(searchResults)

      // Navigate to search results page
      push('/search')
    } catch (error) {
      console.error(error)
    } finally {
      // Reset click state regardless of success/failure
      clicked = false
    }
  }
</script>

<!-- Main search bar container -->
<div class="w-full bg-gray-900 text-white shadow-md px-4 py-3 flex items-center justify-center">
  <!-- Search input field -->
  <input
    type="search"
    placeholder="Search for music"
    bind:value={searchQuery}
    class="p-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500"
  />

  <!-- Search button -->
  <button
    onclick={searchYoutube}
    class="ml-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium cursor-pointer transition"
  >
    Search
  </button>
</div>
