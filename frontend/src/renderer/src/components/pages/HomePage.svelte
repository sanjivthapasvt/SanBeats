<script lang="ts">
  import { onMount } from 'svelte'
  import axios from 'axios'
  import { handlePlay } from '../services/musicService'

  import {
    baseUrl,
    trendingMusic,
    clicked,
    currentTrackId,
    popularMusic
  } from '../stores/Variables'
  import { Play, Loader2, RefreshCw, CircleArrowRight, CircleArrowLeft } from '@lucide/svelte'

  // Fetch trending music from API
  const fetchTrending = async () => {
    try {
      isLoading = true
      const response = await axios.get(`${baseUrl}/trending`)
      trendingMusic.set(response?.data)
    } catch (error) {
      console.error('Error fetching trending music:', error)
    } finally {
      isLoading = false
    }
  }

  let isLoading = true

  let trendingPage = 0
  let popularPage = 0
  const ITEMS_PER_PAGE = 5

  $: trendingPages = Math.ceil($trendingMusic.length / ITEMS_PER_PAGE)
  $: popularPages = Math.ceil($popularMusic.length / ITEMS_PER_PAGE)

  const nextTrending = () => {
    if (trendingPage < trendingPages - 1) trendingPage++
  }
  const prevTrending = () => {
    if (trendingPage > 0) trendingPage--
  }

  const nextPopular = () => {
    if (popularPage < popularPages - 1) popularPage++
  }
  const prevPopular = () => {
    if (popularPage > 0) popularPage--
  }

  const fetchPopular = async () => {
    try {
      const response = await axios.get(`${baseUrl}/most_viewed_music`)
      popularMusic.set(response?.data)
    } catch (error) {
      console.error(error)
    }
  }

  // Load trending music and popular on component mount
  onMount(() => {
    fetchTrending()
    fetchPopular()
    window.scrollTo(0, 0);
  })
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-950 text-white">
  <!-- Trending Section -->
  <div class="px-6 py-16">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-10">
        <h2
          class="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent"
        >
          🔥 Trending Now
        </h2>
        <button
          on:click={fetchTrending && fetchPopular}
          class="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 transition"
        >
          <RefreshCw size={22} />
          <span class="font-medium">Refresh</span>
        </button>
      </div>

      {#if isLoading}
        <div class="relative">
          <button
            on:click={prevTrending}
            class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 w-12 h-12 bg-gray-700 hover:bg-gray-600 rounded-full disabled:opacity-30 flex items-center justify-center"
            disabled={trendingPage === 0}
          >
            <CircleArrowLeft size={20} />
          </button>
          <button
            on:click={nextTrending}
            class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 w-12 h-12 bg-indigo-600 hover:bg-indigo-700 rounded-full disabled:opacity-30 flex items-center justify-center"
            disabled={trendingPage >= trendingPages - 1}
          >
            <CircleArrowRight size={20} />
          </button>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {#each Array(5) as _}
              <div class="bg-gray-800/40 rounded-xl p-6 animate-pulse space-y-4 shadow-md">
                <div class="w-full h-48 bg-gray-700 rounded-lg"></div>
                <div class="h-4 w-3/4 bg-gray-700 rounded"></div>
                <div class="h-3 w-2/3 bg-gray-700 rounded"></div>
              </div>
            {/each}
          </div>
        </div>
      {:else if $trendingMusic.length > 0}
        <div class="relative">
          <button
            on:click={prevTrending}
            class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 w-12 h-12 bg-gray-700 hover:bg-gray-600 rounded-full disabled:opacity-30 flex items-center justify-center"
            disabled={trendingPage === 0}
          >
            <CircleArrowLeft size={20} />
          </button>
          <button
            on:click={nextTrending}
            class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 w-12 h-12 bg-indigo-600 hover:bg-indigo-700 rounded-full disabled:opacity-30 flex items-center justify-center"
            disabled={trendingPage >= trendingPages - 1}
          >
            <CircleArrowRight size={20} />
          </button>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {#each $trendingMusic.slice(trendingPage * ITEMS_PER_PAGE, (trendingPage + 1) * ITEMS_PER_PAGE) as track, index}
              <div
                role="button"
                tabindex="0"
                on:click={() => handlePlay(track.id)}
                on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePlay(track.id)}
                class="group bg-gray-900/40 rounded-xl cursor-pointer p-4 backdrop-blur-sm hover:bg-gray-900/60 border border-gray-700/30 transition transform hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              >
                <div class="relative mb-4 overflow-hidden rounded-lg group">
                  <img
                    src={track.thumbnail}
                    alt={track.title}
                    class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-110 rounded-lg"
                  />
                  <div
                    class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  >
                    {#if $clicked && $currentTrackId === track.id}
                      <Loader2 class="w-10 h-10 text-white animate-spin" />
                    {:else}
                      <Play class="w-12 h-12 text-white" />
                    {/if}
                  </div>
                  <div
                    class="absolute top-2 left-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold px-2 py-1 rounded-full"
                  >
                    #{index + 1 + trendingPage * ITEMS_PER_PAGE}
                  </div>
                  <div
                    class="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-medium"
                  >
                    {track.duration}
                  </div>
                </div>
                <div>
                  <h3 class="text-lg font-semibold truncate group-hover:text-indigo-300 transition">
                    {track.title}
                  </h3>
                  <p class="text-sm text-gray-400 truncate">{track.channel}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {:else}
        <div class="text-center py-20">
          <div class="text-7xl mb-4">😕</div>
          <h3 class="text-2xl font-bold mb-2">No trending music found</h3>
          <p class="text-gray-400 mb-6">Try refreshing or come back later.</p>
          <button
            on:click={fetchTrending}
            class="bg-indigo-500 hover:bg-indigo-600 px-6 py-2 text-sm font-semibold rounded-full transition duration-300"
            >Retry</button
          >
        </div>
      {/if}
    </div>
  </div>

  <!-- Popular Section -->
  <div class="px-6 py-16">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-10">
        <h2
          class="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent"
        >
          🔥 Popular Music
        </h2>
      </div>

      {#if isLoading}
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          {#each Array(5) as _}
            <div class="bg-gray-800/40 rounded-xl p-6 animate-pulse space-y-4 shadow-md">
              <div class="w-full h-48 bg-gray-700 rounded-lg"></div>
              <div class="h-4 w-3/4 bg-gray-700 rounded"></div>
              <div class="h-3 w-2/3 bg-gray-700 rounded"></div>
            </div>
          {/each}
        </div>
      {:else if $popularMusic.length > 0}
        <div class="relative">
          <!-- Prev Button -->
          <button
            on:click={prevPopular}
            class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 w-12 h-12 bg-gray-700 hover:bg-gray-600 rounded-full disabled:opacity-30 flex items-center justify-center"
            disabled={popularPage === 0}
          >
            <CircleArrowLeft size={20} />
          </button>

          <!-- Next Button -->
          <button
            on:click={nextPopular}
            class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 w-12 h-12 bg-indigo-600 hover:bg-indigo-700 rounded-full disabled:opacity-30 flex items-center justify-center"
            disabled={popularPage >= popularPages - 1}
          >
            <CircleArrowRight size={20} />
          </button>

          <!-- Grid of Music Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {#each $popularMusic.slice(popularPage * ITEMS_PER_PAGE, (popularPage + 1) * ITEMS_PER_PAGE) as track, index}
              <div
                role="button"
                tabindex="0"
                on:click={() => handlePlay(track.id)}
                on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePlay(track.id)}
                class="group bg-gray-900/40 rounded-xl cursor-pointer p-4 backdrop-blur-sm hover:bg-gray-900/60 border border-gray-700/30 transition transform hover:scale-105 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              >
                <div class="relative mb-4 overflow-hidden rounded-lg group">
                  <img
                    src={track.thumbnail}
                    alt={track.title}
                    class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-110 rounded-lg"
                  />
                  <div
                    class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  >
                    {#if $clicked && $currentTrackId === track.id}
                      <Loader2 class="w-10 h-10 text-white animate-spin" />
                    {:else}
                      <Play class="w-12 h-12 text-white" />
                    {/if}
                  </div>
                  <div
                    class="absolute top-2 left-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold px-2 py-1 rounded-full"
                  >
                    #{index + 1 + popularPage * ITEMS_PER_PAGE}
                  </div>
                  <div
                    class="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-medium"
                  >
                    {track.duration}
                  </div>
                </div>
                <div>
                  <h3 class="text-lg font-semibold truncate group-hover:text-indigo-300 transition">
                    {track.title}
                  </h3>
                  <p class="text-sm text-gray-400 truncate">{track.channel}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {:else}
        <div class="text-center py-20">
          <div class="text-7xl mb-4">😕</div>
          <h3 class="text-2xl font-bold mb-2">No popular music found</h3>
          <p class="text-gray-400 mb-6">Try refreshing or come back later.</p>
          <button
            on:click={fetchTrending}
            class="bg-indigo-500 hover:bg-indigo-600 px-6 py-2 text-sm font-semibold rounded-full transition duration-300"
            >Retry</button
          >
        </div>
      {/if}
    </div>
  </div>
</div>
