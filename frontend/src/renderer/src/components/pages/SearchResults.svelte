<script lang="ts">
  import { searchResults } from '../stores/search'
  import { decode } from 'he';
</script>

<div class="p-6 max-w-7xl mx-auto">
  {#if $searchResults.length > 0}
    <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
      <h2 class="text-2xl font-semibold text-gray-900">Search Results</h2>
    </div>
    
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each $searchResults as item}
        <div class="group bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:shadow-xl hover:border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" role="button" tabindex="0">
          <div class="relative h-40 overflow-hidden">
            <img 
              src={item.thumbnail} 
              alt={item.title}
              loading="lazy"
              class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div class="absolute bottom-2 right-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-medium">
              {item.duration}
            </div>
          </div>
          
          <div class="p-4 flex-1">
            <h3 class="text-sm font-semibold text-gray-900 mb-1 line-clamp-2 leading-5" title={item.title}>
              {decode(item.title)}
            </h3>
            <p class="text-xs text-gray-500 truncate" title={item.channel}>
              {item.channel}
            </p>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-center py-16 px-6">
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No tracks found</h3>
      <p class="text-gray-500">Try adjusting your search terms or browse our featured playlists</p>
    </div>
  {/if}
</div>