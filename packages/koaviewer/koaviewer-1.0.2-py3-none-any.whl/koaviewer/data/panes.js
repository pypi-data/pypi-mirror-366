function pane_init() {
  const panes = document.querySelectorAll('.pane');

  let z = 1;

  panes.forEach((pane) => {

    const title  = pane.querySelector('.title');
    const corner = pane.querySelector('.corner');


    /* Title mouse down */

    title.addEventListener('mousedown', (event) => {

      z = z + 1;

      pane.style.zIndex = z;
      pane.classList.add('is-dragging');

      let l = pane.offsetLeft;
      let t = pane.offsetTop;

      let startX = event.pageX;
      let startY = event.pageY;


      /* Title mouse drag */

      const drag = (event) => {
        event.preventDefault();

        var winWidth  = window.innerWidth
        var winHeight = window.innerHeight

        if(event.pageX > 30 
        && event.pageY >  0
        && event.pageX < winWidth-30 
        && event.pageY < winHeight-30)
        {
          pane.style.left = l + (event.pageX - startX) + 'px';
          pane.style.top  = t + (event.pageY - startY) + 'px';
        }
      }


      /* Title mouse Up */

      const mouseup = () => {
        pane.classList.remove('is-dragging');

        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup',   mouseup);
      }


      document.addEventListener('mousemove', drag);
      document.addEventListener('mouseup',   mouseup);
    })


    /* ------------------------------------------------` */


    /* Corner mouse down */

    corner.addEventListener('mousedown', (event) => {

      let w = pane.clientWidth;
      let h = pane.clientHeight;

      let startX = event.pageX;
      let startY = event.pageY;

      z = z + 1;

      pane.style.zIndex = z;


      /* Corner mouse drag */

      const drag = (event) => {
        event.preventDefault();

        var winWidth  = window.innerWidth
        var winHeight = window.innerHeight

        if(event.pageX > 5 
        && event.pageY > 5
        && event.pageX < winWidth-5 
        && event.pageY < winHeight-5)
        {
          pane.style.width  = w + (event.pageX - startX) + 'px';
          pane.style.height = h + (event.pageY - startY) + 'px';
        }
      }


      /* Corner mouse up */

      const mouseup = () => {
        document.removeEventListener('mousemove', drag);
        document.removeEventListener('mouseup',   mouseup);
      }

      document.addEventListener('mousemove', drag);
      document.addEventListener('mouseup',   mouseup);
    })
  })
}
