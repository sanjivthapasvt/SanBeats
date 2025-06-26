<script lang="ts">
  import { Video, Music, Download, Loader2 } from '@lucide/svelte'
  import { downloadVideo } from '../services/downloadService'

  let video_url: string = ''
  let path: string = '~/Downloads/SanBeats'
  let typeString: string = 'video'
  let quality: number = 1080
  let isLoading: boolean = false
  $: video = typeString === 'video'

  let message: string = ''
  let messageType: 'success' | 'error' | '' = ''

  const handleSubmit = async (event: Event) => {
    event.preventDefault()
    isLoading = true
    try {
      await downloadVideo(video_url, path, video, quality)
      message = 'Download completed successfully!'
      messageType = 'success'
    } catch (error) {
      message = 'Download failed. Please check the URL and try again.'
      messageType = 'error'
    } finally {
      isLoading = false
    }
  }
</script>

<div
  class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4"
>
  <div class="w-full max-w-md">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">SanBeats Downloader</h1>
    </div>

    <!-- Main Form Card -->
    <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        <!-- URL Input -->
        <div class="space-y-2">
          <label for="video_url" class="block text-sm font-semibold text-gray-700">
            Video URL
          </label>
          <input
            type="url"
            id="video_url"
            bind:value={video_url}
            required
            placeholder="https://youtube.com/video"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
          />
        </div>

        <div class="space-y-2">
          <label for="path" class="block text-sm font-semibold text-gray-700">
            Download Path
          </label>
          <input
            type="text"
            id="path"
            bind:value={path}
            class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
          />
        </div>

        <!-- Type Selection -->
        <div class="space-y-3">
          <!-- svelte-ignore a11y_label_has_associated_control -->
          <label class="block text-sm font-semibold text-gray-700"> Download Type </label>
          <div class="flex space-x-4">
            <label class="flex items-center space-x-3 cursor-pointer group">
              <input
                type="radio"
                bind:group={typeString}
                value="video"
                class="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span
                class="text-gray-700 group-hover:text-blue-600 transition-colors duration-200 flex items-center space-x-2"
              >
                <Video class="w-5 h-5" />
                <span>Video</span>
              </span>
            </label>

            <label class="flex items-center space-x-3 cursor-pointer group">
              <input
                type="radio"
                bind:group={typeString}
                value="audio"
                class="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span
                class="text-gray-700 group-hover:text-blue-600 transition-colors duration-200 flex items-center space-x-2"
              >
                <Music class="w-5 h-5" />
                <span>Audio</span>
              </span>
            </label>
          </div>
        </div>

        <!-- Quality Selection (only for video) -->
        {#if video}
          <div class="space-y-2">
            <label for="quality" class="block text-sm font-semibold text-gray-700">
              Video Quality
            </label>
            <select
              name="quality"
              id="quality"
              bind:value={quality}
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 focus:bg-white"
            >
              <option value={1080}>1080p (Full HD)</option>
              <option value={720}>720p (HD)</option>
              <option value={480}>480p (SD)</option>
            </select>
          </div>
        {/if}

        <!-- Submit Button -->
        <button
          type="submit"
          disabled={isLoading || !video_url.trim()}
          class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
        >
          {#if isLoading}
            <Loader2 class="animate-spin w-5 h-5" />
            <span>Downloading...</span>
          {:else}
            <Download class="w-5 h-5" />
            <span>Download</span>
          {/if}
        </button>
      </form>
    </div>
    {#if message}
      <p
        class={`mt-4 text-center font-semibold ${
          messageType === 'success' ? 'text-green-600' : 'text-red-600'
        }`}
      >
        {message}
      </p>
    {/if}
  </div>
</div>
