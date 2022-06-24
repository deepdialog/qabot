
import { Link } from 'react-router-dom'
import { Button } from 'antd'


export function Header(props) {
    const buttonStyle = {
        marginRight: '10px',
        padding: '10px',
    }
    return (
        <div style={{paddingBottom: '20px'}}>
            <Link to={`/home/${props.token}`} style={buttonStyle}>
                <Button>
                    首页
                </Button>
            </Link>
            <Link to={`/ask/${props.token}`} style={buttonStyle}>
                <Button>
                    问答测试
                </Button>
            </Link>
            <Link to={`/batch/${props.token}`} style={buttonStyle}>
                <Button>
                    批量添加
                </Button>
            </Link>
        </div>
    )
}
