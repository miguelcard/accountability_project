export const isAuthentication = () => {
    let store =  localStorage.getItem('storage');
    store = JSON.parse(store)

    if (store === null) {
        return false
    }
    if (store && store.authentication.token) {
        return true
    }
    return false
}
