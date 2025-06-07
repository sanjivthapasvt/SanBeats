<script lang="ts">
  import { onMount } from 'svelte'
  import { SkipBack, SkipForward, CirclePause, CirclePlay, Loader2, Play } from '@lucide/svelte'
  import { recommendedMusic, clicked, currentTrackId, audioInfoResults } from '../stores/Variables'
  import { handlePlay } from '../services/musicService'
  import { decode } from 'he'

  let audioElement: HTMLAudioElement
  let isPlaying = false
  let currentTime = 0
  let duration = 0

  onMount(() => {
    if (audioElement) {
      audioElement.addEventListener('loadedmetadata', () => {
        duration = audioElement.duration
      })

      audioElement.addEventListener('timeupdate', () => {
        currentTime = audioElement.currentTime
      })

      audioElement.addEventListener('ended', () => {
        isPlaying = false
      })
    }
    togglePlay()
  })

  function togglePlay() {
    if (audioElement) {
      if (isPlaying) {
        audioElement.pause()
      } else {
        audioElement.play()
      }
      isPlaying = !isPlaying
    }
  }

  function handleSeek(event: Event) {
    const target = event.target as HTMLInputElement
    const newTime = (parseFloat(target.value) / 100) * duration
    if (audioElement) {
      audioElement.currentTime = newTime
    }
  }

  function formatTime(time: number): string {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  function getProgressPercentage(): number {
    return duration ? (currentTime / duration) * 100 : 0
  }
</script>

<div
  class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-950 text-white flex"
>
  <!--  Player Section - Left Side -->

  <div
    class="w-[50%] fixed left-0 top-0 bottom-0 flex items-center justify-center p-6 overflow-y-auto"
  >
    {#if $audioInfoResults}
      <div class="w-full max-w-2xl">
        <!-- Hidden Audio Element -->
        <audio bind:this={audioElement} src={$audioInfoResults.url} preload="metadata"></audio>

        <!-- Player Card -->
        <div
          class="bg-gray-900/40 backdrop-blur-sm rounded-xl shadow-2xl border border-gray-700/30 overflow-hidden hover:bg-gray-900/60 transition-all duration-300"
        >
          <!-- Artwork  -->
          <div class="relative">
            <div class="aspect-video w-full">
              <img
                src={$audioInfoResults.thumbnail}
                alt="Audio thumbnail"
                class="w-full h-full object-cover"
              />
              <div
                class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"
              ></div>
            </div>
          </div>

          <!-- Content -->
          <div class="p-4">
            <h1
              class="text-lg font-semibold mb-1 line-clamp-2 text-white group-hover:text-indigo-300 transition"
            >
              {$audioInfoResults.title}
            </h1>

            <div class="flex items-center gap-3 mb-4 text-sm text-gray-400">
              <span
                class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-2 py-1 rounded text-xs font-medium"
              >
                {$audioInfoResults.format?.toUpperCase() || 'AUDIO'}
              </span>
              <span>{$audioInfoResults.quality}</span>
            </div>

            <!-- Time & Progress -->
            <div class="mb-4">
              <div class="flex justify-between text-xs text-gray-400 mb-1">
                <span class="font-mono">{formatTime(currentTime)}</span>
                <span class="font-mono">{duration ? formatTime(duration) : '--:--'}</span>
              </div>
              <div class="relative">
                <div class="h-1 bg-gray-700/50 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full"
                    style="width: {getProgressPercentage()}%"
                  ></div>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={getProgressPercentage()}
                  on:input={handleSeek}
                  class="absolute top-1/2 left-0 w-full h-4 cursor-pointer appearance-none bg-transparent transform -translate-y-1/2"
                />
              </div>
            </div>

            <!-- Controls -->
            <div class="flex justify-center items-center gap-6">
              <button
                class="p-2 text-gray-400 hover:text-white rounded-full hover:bg-gray-700/30 transition"
              >
                <SkipBack size={22} />
              </button>

              <button
                on:click={togglePlay}
                class="p-3 rounded-full bg-indigo-600 hover:bg-indigo-700 transition text-white shadow"
              >
                {#if isPlaying}
                  <CirclePause size={26} />
                {:else}
                  <CirclePlay size={26} />
                {/if}
              </button>

              <button
                class="p-2 text-gray-400 hover:text-white rounded-full hover:bg-gray-700/30 transition"
              >
                <SkipForward size={22} />
              </button>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Scrollable Recommendations Section - Right Side -->
  <div class="w-[50%] ml-auto">
    <div class="p-6">
      <!-- Header -->
      <div
        class="mb-6 sticky top-0 bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-950 py-4 z-10 border-b border-gray-700/30 rounded-xl"
      >
        <h2
          class="pl-3 text-2xl font-extrabold tracking-tight bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent"
        >
          Recommended for you
        </h2>
      </div>

      {#if $recommendedMusic.length > 0}
        <!-- Recommendations List -->
        <div class="space-y-3">
          {#each $recommendedMusic as track}
            <div
              role="button"
              tabindex="0"
              on:click={() => handlePlay(track.id)}
              on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && handlePlay(track.id)}
              class="group flex items-start gap-3 p-3 rounded-lg bg-gray-900/40 backdrop-blur-sm hover:bg-gray-900/60 transition-all duration-200 cursor-pointer border border-gray-700/30 hover:border-indigo-500/30 hover:shadow-lg transform hover:scale-[1.02]"
            >
              <!-- Thumbnail -->
              <div class="relative flex-shrink-0">
                <div class="w-24 h-16 rounded-md overflow-hidden bg-gray-700/50">
                  <img
                    src={track.thumbnail}
                    alt={track.title}
                    loading="lazy"
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                </div>

                <!-- Play Overlay -->
                <div
                  class="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-md"
                >
                  {#if $clicked && $currentTrackId === track.id}
                    <Loader2 class="w-4 h-4 text-white animate-spin" />
                  {:else}
                    <Play class="w-4 h-4 text-white fill-current" />
                  {/if}
                </div>

                <!-- Duration Badge -->
                <div
                  class="absolute bottom-1 right-1 bg-black/80 text-white px-1.5 py-0.5 rounded text-xs font-medium"
                >
                  {track.duration}
                </div>
              </div>

              <!-- Track Info -->
              <div class="flex-1 min-w-0 pt-1">
                <h3
                  class="text-sm font-semibold text-white line-clamp-2 leading-5 group-hover:text-indigo-300 transition-colors mb-1"
                >
                  {decode(track.title)}
                </h3>
                <p
                  class="text-xs text-gray-400 line-clamp-1 group-hover:text-gray-300 transition-colors"
                >
                  {track.channel}
                </p>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <!-- Empty State -->
        <div class="text-center py-20">
          <div
            class="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <span class="text-2xl">🎵</span>
          </div>
          <h3 class="text-lg font-semibold text-white mb-2">No recommendations yet</h3>
          <p class="text-sm text-gray-400">We'll show you music recommendations here</p>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .line-clamp-1 {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
