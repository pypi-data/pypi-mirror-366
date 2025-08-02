function leftHandler() {
    // Go to previous image
    pauseCurrent()
    const current = document.getElementById(window.location.hash.slice(1))
    const next = current?.previousElementSibling
        ? current.previousElementSibling
        : document.getElementById('canvas').lastElementChild
    location.replace(`#${next.id}`)
    preloadSurrounding()
}

function rightHandler() {
    // Go to next image
    pauseCurrent()
    const current = document.getElementById(window.location.hash.slice(1))
    const next = current?.nextElementSibling
        ? current.nextElementSibling
        : document.getElementById('canvas').firstElementChild
    location.replace(`#${next.id}`)
    preloadSurrounding()
}

function upHandler() {
    // Go to first image
    pauseCurrent()
    const next = document.getElementById('canvas').firstElementChild
    location.replace(`#${next.id}`)
    preloadSurrounding()
}

function downHandler() {
    // Go to last image
    pauseCurrent()
    const next = document.getElementById('canvas').lastElementChild
    location.replace(`#${next.id}`)
    preloadSurrounding()
}

function preloadSurrounding() {
    // Eagerly load images around current
    const current = document.getElementById(window.location.hash.slice(1))
    const previous = current?.previousElementSibling
        ? current.previousElementSibling
        : document.getElementById('canvas').lastElementChild
    previous?.querySelector('img')?.setAttribute('loading', 'eager')
    const next = current?.nextElementSibling
        ? current.nextElementSibling
        : document.getElementById('canvas').firstElementChild
    next?.querySelector('img')?.setAttribute('loading', 'eager')
}

function highlightThumbnail() {
    // Highlight the thumbnail corresponding to the displayed image
    const current = document.getElementById('thumbnails').querySelector('.current')
    current?.classList.remove('current')
    const next = document.querySelector(`[data-id="${window.location.hash.slice(1)}"]`)
    next?.classList.add('current')
}

function pauseCurrent() {
    // Pause a video when navigating to another image
    const current = document.getElementById(window.location.hash.slice(1))
    current?.querySelector('video')?.pause()
}

function nextPrevious(event) {
    // Detect clicks on left/right side of currently displayed image to go to next/previous
    if (event.currentTarget.querySelector(':target video')) {
        return false
    }
    const offset = event.offsetX - (event.target.offsetWidth / 2)
    const deadzone = event.target.offsetWidth / 10
    if (offset > deadzone) {
        rightHandler()
    }
    else if (offset < -deadzone) {
        leftHandler()
    }
}

function toggleFullscreen() {
    // Toggle fullscreen for the canvas
    if (document.fullscreenElement) {
        document.exitFullscreen()
    }
    else {
        const canvas = document.getElementById('canvas')
        canvas.requestFullscreen({navigationUI: 'hide'})
    }
}

function keyHandler(event) {
    // Handle navigation by keys
    const callback = {
        'ArrowLeft': leftHandler,
        'ArrowRight': rightHandler,
        'ArrowUp': upHandler,
        'ArrowDown': downHandler,
        'f': toggleFullscreen,
    }[event.key]
    callback?.()
}

// Do not add handlers if there is no content
const canvas = document.getElementById('canvas')
if (canvas) {
    const first_entry = canvas.firstElementChild
    document.addEventListener('keydown', keyHandler)
    window.addEventListener('hashchange', highlightThumbnail)
    canvas.addEventListener('click', nextPrevious)

    const fullscreen = document.getElementById('fullscreen')
    if (document.fullscreenEnabled) {
        fullscreen.addEventListener('click', toggleFullscreen)
    }
    else {
        fullscreen.remove()
    }

    if (!window.location.hash.slice(1)) {
        upHandler()
    }
    highlightThumbnail()
    preloadSurrounding()
}
