<script>
  import Router from 'svelte-spa-router'
  import HomePage from './components/pages/HomePage.svelte'
  import SearchBar from './components/navigation/SearchBar.svelte'
  import SearchResults from './components/pages/SearchResults.svelte'

  const routes = {
    '/': HomePage,
    '/search': SearchResults
  }
</script>

<SearchBar />
<Router {routes} />
