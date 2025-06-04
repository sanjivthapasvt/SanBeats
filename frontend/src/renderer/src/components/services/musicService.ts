import axios from 'axios'
import { baseUrl, recommendedMusic, audioInfoResults } from '../stores/Variables'
import { push } from 'svelte-spa-router'
import { clicked, currentTrackId } from '../stores/Variables'
import { get } from 'svelte/store'

// Handle play button click - fetch track info and navigate
export const handlePlay = async (videoId: string): Promise<void> => {
  if (get(clicked)) return // Prevent multiple simultaneous requests
  clicked.set(true)
  currentTrackId.set(videoId)

  try {
    const response = await axios.get(`${baseUrl}/info/${videoId}`)
    audioInfoResults.set(response?.data)
    await getRecommendation(videoId)
    push('/play') // Navigate to player page
  } catch (error) {
    console.error(error)
  } finally {
    clicked.set(false)
    currentTrackId.set(null)
  }
}

export const getRecommendation = async (videoId: string): Promise<void> => {
  try {
    const response = await axios.get(`${baseUrl}/recommendation/${videoId}`)
    recommendedMusic.set(response?.data)
  } catch (error) {
    console.error(error)
  }
}
