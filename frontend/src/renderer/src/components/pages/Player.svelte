<script lang="ts">
  import { audioInfoResults } from '../stores/Variables'
  import { onMount } from 'svelte'
  import { SkipBack, SkipForward, CirclePause, CirclePlay } from '@lucide/svelte'

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

<div class="p-6 max-w-4xl mx-auto font-sans">
  {#if $audioInfoResults}
    <div class="bg-gray-900 rounded-2xl shadow-lg border border-gray-800 overflow-hidden">
      <!-- Hidden Audio Element -->
      <audio bind:this={audioElement} src={$audioInfoResults.url} preload="metadata"></audio>

      <!-- Main Player Container -->
      <div class="relative">
        <!-- Background Image with Overlay -->
        <div class="absolute inset-0 opacity-10">
          <img
            src={$audioInfoResults.thumbnail}
            alt="Audio thumbnail"
            class="w-full h-full object-cover"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-gray-900/90 to-transparent"></div>
        </div>

        <!-- Content -->
        <div class="relative z-10 p-6 sm:p-8">
          <!-- Top Section: Artwork and Info -->
          <div class="flex flex-col md:flex-row gap-6 mb-8">
            <!-- Artwork -->
            <div class="flex-shrink-0 mx-auto md:mx-0">
              <div
                class="w-40 h-40 sm:w-48 sm:h-48 rounded-lg overflow-hidden shadow-md ring-1 ring-gray-700"
              >
                <img
                  src={$audioInfoResults.thumbnail}
                  alt="Audio thumbnail"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>

            <!-- Track Info -->
            <div class="flex-1 text-center md:text-left">
              <h1 class="text-2xl sm:text-3xl font-semibold text-white mb-3 leading-tight">
                {$audioInfoResults.title}
              </h1>

              <!-- Audio Details -->
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div class="bg-gray-800/50 rounded-lg p-3">
                  <div class="text-gray-400 text-xs font-medium uppercase">Duration</div>
                  <div class="text-white text-sm font-medium">{$audioInfoResults.duration}</div>
                </div>
                <div class="bg-gray-800/50 rounded-lg p-3">
                  <div class="text-gray-400 text-xs font-medium uppercase">Format</div>
                  <div class="text-white text-sm font-medium uppercase">
                    {$audioInfoResults.format}
                  </div>
                </div>
                <div class="bg-gray-800/50 rounded-lg p-3 col-span-2 sm:col-span-1">
                  <div class="text-gray-400 text-xs font-medium uppercase">Quality</div>
                  <div class="text-white text-sm font-medium">{$audioInfoResults.quality}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="mb-6">
            <div class="flex items-center gap-4 text-white text-sm">
              <span class="min-w-[40px] tabular-nums font-mono">{formatTime(currentTime)}</span>
              <div class="flex-1 relative">
                <div class="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-red-400 rounded-full transition-all duration-75"
                    style="width: {getProgressPercentage()}%"
                  ></div>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={getProgressPercentage()}
                  on:input={handleSeek}
                  class="absolute top-1/2 left-0 w-full h-4 cursor-pointer appearance-none bg-transparent range-slider transform -translate-y-1/2"
                />
              </div>
              <span class="min-w-[40px] tabular-nums font-mono">
                {duration ? formatTime(duration) : '--:--'}
              </span>
            </div>
          </div>

          <!-- Controls -->
          <div class="flex items-center justify-center gap-8">
            <!-- Previous Button -->
            <button
              class="text-gray-300 hover:text-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500 rounded-full"
              aria-label="Previous track"
            >
              <SkipBack size={28} />
            </button>

            <!-- Play/Pause Button -->
            <button
              on:click={togglePlay}
              class="text-white hover:text-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500 rounded-full"
              aria-label={isPlaying ? 'Pause' : 'Play'}
            >
              {#if isPlaying}
                <CirclePause size={40} />
              {:else}
                <CirclePlay size={40} />
              {/if}
            </button>

            <!-- Next Button -->
            <button
              class="text-gray-300 hover:text-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-500 rounded-full"
              aria-label="Next track"
            >
              <SkipForward size={28} />
            </button>
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="bg-gray-800 rounded-2xl p-10 text-center shadow-md border border-gray-700">
      <h2 class="text-xl font-semibold text-white mb-2">No Audio Selected</h2>
      <p class="text-gray-400 text-sm">Choose an audio file to start playing</p>
    </div>
  {/if}
</div>

<style>
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background-color: #ef4444;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.range-slider::-webkit-slider-track {
  background: transparent;
  height: 4px;
}

.range-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background-color: #ef4444;
  border: 2px solid white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.range-slider::-moz-range-track {
  background: transparent;
  height: 4px;
}

.range-slider::-ms-thumb {
  width: 16px;
  height: 16px;
  background-color: #ef4444;
  border: 2px solid white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.range-slider::-ms-track {
  background: transparent;
  height: 4px;
  border: none;
  color: transparent;
}

.range-slider::-ms-fill-lower,
.range-slider::-ms-fill-upper {
  background: transparent;
}
</style>