<script lang="ts">
  import logo from '../../assets/SanBeats.png'
  import axios from 'axios'
  const baseUrl = 'http://localhost:8000/api'
  let searchQuery = ''
  let searchResult = []
  const searchYoutube = async () => {
    try {
      const response = await axios.get(`${baseUrl}/search`, {
        params: {
          q: searchQuery
        }
      })
      searchResult = response?.data
      console.log(searchResult)
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

<div class="min-h-screen bg-gray-800 text-white flex flex-col items-center justify-center p-6">
  <img src={logo} alt="logo" class="w-25 h-25 text-indigo-500 mb-4" />
  <h1 class="text-3xl font-bold mb-2">Welcome, to SanBeats</h1>
  <p class="text-lg text-gray-300">Search for music to get started</p>
</div>
