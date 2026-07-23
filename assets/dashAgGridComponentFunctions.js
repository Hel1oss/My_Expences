var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


dagcomponentfuncs.DeleteButton = function (props) {
    function onClick() {
        const rowId = props.node.data.id;


        props.setData({
            id: rowId
        });


        props.api.applyTransaction({
            remove: [props.node.data]
        });
    }
    return React.createElement('button',
            {
                onClick,
                className: 'trash-btn',
                style: {
                width: '24px',
                height: '24px',
                borderRadius: '30%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '0',
                margin: '0',
                lineHeight: '1',
                border: '1px solid #707070',
                cursor: 'pointer',

                backgroundColor: "#31313113"
                }
            },
            React.createElement('img', {
            src: '/assets/Trash.svg',
            className: 'trash-logo',
            style: {
                width: '14px',
                height: '14px',
                filter: 'brightness(0) invert(0.5)'
            }
        })
    );
};