<script>
  import Router from 'svelte-spa-router'
  import HomePage from './components/pages/HomePage.svelte'
  import SearchBar from './components/navigation/SearchBar.svelte'
  import SearchResults from './components/pages/SearchResults.svelte'
  import Playing from './components/pages/Player.svelte';

  const routes = {
    '/': HomePage,
    '/search': SearchResults,
    '/play': Playing,
  }
</script>

<SearchBar />
<Router {routes} />
