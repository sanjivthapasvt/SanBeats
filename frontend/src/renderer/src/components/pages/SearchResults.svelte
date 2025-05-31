<script lang="ts">
  // Import necessary dependencies
  import { searchResults } from '../stores/Variables'
  import { decode } from 'he'
  import { clicked, currentTrackId } from '../stores/Variables'
  import { Play, Loader2 } from '@lucide/svelte'
  import { handlePlay } from '../services/musicService'
</script>

<!-- Main container with dark gradient background -->
<div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-950 text-white">
  <div class="px-6 py-16">
    <div class="max-w-7xl mx-auto">
      <!-- Show results if search results exist -->
      {#if $searchResults.length > 0}
        <!-- Header section with title -->
        <div class="flex justify-between items-center mb-10">
          <h2
            class="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent"
          >
            🔍 Search Results
          </h2>
          <div class="text-sm text-gray-400">
            {$searchResults.length} tracks found
          </div>
        </div>

        <!-- Modern grid layout matching trending music design -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <!-- Loop through each search result -->
          {#each $searchResults as track}
            <!-- Individual result card with modern styling -->
            <div
              role="button"
              tabindex="0"
              on:click={() => handlePlay(track.id)}
              on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePlay(track.id)}
              class="group bg-gray-900/40 rounded-xl cursor-pointer p-4 backdrop-blur-sm hover:bg-gray-900/60 border border-gray-700/30 transition transform hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              <!-- Thumbnail section with play overlay -->
              <div class="relative mb-4 overflow-hidden rounded-lg group">
                <!-- Thumbnail image -->
                <img
                  src={track.thumbnail}
                  alt={track.title}
                  loading="lazy"
                  class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-110 rounded-lg"
                />

                <!-- Play button overlay on hover -->
                <div
                  class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                >
                  {#if $clicked && $currentTrackId === track.id}
                    <Loader2 class="w-10 h-10 text-white animate-spin" />
                  {:else}
                    <Play class="w-12 h-12 text-white" />
                  {/if}
                </div>

                <!-- Duration -->
                <div
                  class="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-medium"
                >
                  {track.duration}
                </div>
              </div>

              <!-- Track details -->
              <div>
                <h3
                  class="text-lg font-semibold truncate group-hover:text-indigo-300 transition"
                  title={track.title}
                >
                  {decode(track.title)}
                </h3>
                <p class="text-sm text-gray-400 truncate" title={track.channel}>
                  {track.channel}
                </p>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <!-- Empty state when no search results are found -->
        <div class="text-center py-20">
          <div class="text-7xl mb-4">🔍</div>
          <h3 class="text-2xl font-bold mb-2">No tracks found</h3>
          <p class="text-gray-400 mb-6">Try adjusting your search term</p>
        </div>
      {/if}
    </div>
  </div>
</div>
