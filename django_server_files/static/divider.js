document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('container');
    const topDiv = document.getElementById('map');
    const divider = document.getElementById('divider');
    const bottomDiv = document.getElementById('eval-graph');

    let isResizing = false;
    const COLLAPSED_HEIGHT = 0;
    const EXPANDED_HEIGHT = 200;

    divider.addEventListener('mousedown', function (e) {
        isResizing = true;
        document.body.style.cursor = 'ns-resize';
    });

    document.addEventListener('mousemove', function (e) {
        if (isResizing) {
            const containerRect = container.getBoundingClientRect();
            const newTopHeight = e.clientY - containerRect.top;
            const newBottomHeight = containerRect.bottom - e.clientY;

            if (newTopHeight > 50 && newBottomHeight > 0) { // Ensure minimum height
                topDiv.style.flexBasis = `${newTopHeight}px`;
                bottomDiv.style.flexBasis = `${newBottomHeight}px`;
            }
        }
    });

    document.addEventListener('mouseup', function () {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = 'default';
        }
    });
});
