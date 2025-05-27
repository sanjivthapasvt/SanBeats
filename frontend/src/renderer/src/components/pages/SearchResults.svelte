<script lang="ts">
  // Import necessary dependencies
  import axios from 'axios'
  import { baseUrl, searchResults } from '../stores/Variables'
  import { decode } from 'he'
  import { audioInfoResults } from '../stores/Variables'
  import { push } from 'svelte-spa-router'

  // State to prevent multiple clicks while loading
  let clicked: boolean = false

  // Handle play button click - fetch audio info and navigate to player
  const handlePlay = async (videoId: string) => {
    try {
      // Prevent multiple simultaneous requests
      if (clicked) return
      clicked = true

      // Fetch audio information from the API
      const response = await axios.get(`${baseUrl}/info/${videoId}`)

      // Store the audio info in the global store
      audioInfoResults.set(response?.data)
      console.log(audioInfoResults)

      // Navigate to the player page
      push('/play')
    } catch (error) {
      console.error(error)
    } finally {
      // Reset click state regardless of success/failure
      clicked = false
    }
  }
</script>

<!-- Main container with responsive padding and max width -->
<div class="p-6 max-w-7xl mx-auto">
  <!-- Show results if search results exist -->
  {#if $searchResults.length > 0}
    <!-- Header section with title -->
    <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
      <h2 class="text-2xl font-semibold text-gray-900">Search Results</h2>
    </div>

    <!-- Responsive grid layout for search results -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <!-- Loop through each search result -->
      {#each $searchResults as item}
        <!-- Individual result card -->
        <div
          role="button"
          tabindex="0"
          on:click={() => handlePlay(item.id)}
          on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePlay(item.id)}
          class="group bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:shadow-xl hover:border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <!-- Thumbnail section -->
          <div class="relative h-40 overflow-hidden">
            <!-- Thumbnail image  -->
            <img
              src={item.thumbnail}
              alt={item.title}
              loading="lazy"
              class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <!-- Duration  -->
            <div
              class="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-medium"
            >
              {item.duration}
            </div>
          </div>

          <!-- Content section with title and channel info -->
          <div class="p-4 flex-1">
            <!-- Track title -->
            <h3
              class="text-sm font-semibold text-gray-900 mb-1 line-clamp-2 leading-5"
              title={item.title}
            >
              {decode(item.title)}
            </h3>
            <!-- Channel namen -->
            <p class="text-xs text-gray-500 truncate" title={item.channel}>
              {item.channel}
            </p>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <!-- When no search results are found -->
    <div class="text-center py-16 px-6">
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No tracks found</h3>
      <p class="text-gray-500">Try adjusting your search terms or browse our featured playlists</p>
    </div>
  {/if}
</div>
