import axios from 'axios'
import { baseUrl } from '../stores/Variables'

export const downloadVideo = async (
  video_url: string,
  path: string,
  video: boolean = true,
  quality: number = null
): Promise<boolean> => {
  try {
    const response = await axios.post(`${baseUrl}/download`, null, {
      params: {
        video_url,
        path,
        video,
        quality
      }
    })

    return response.status === 200 || response.status === 201
  } catch (err) {
    console.error(`Error while downloading: ${err}`)
    throw err
  }
}
