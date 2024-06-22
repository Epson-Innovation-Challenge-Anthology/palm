<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';

  const imageUrls: string[] = [
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/84r0sx0ckf0czcog9rr70qiydn3lbnni.gif",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/5rkzeiqtr69quxy4zb93elea90tvgs1t.jpeg",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/hxw6xdsdqc07gi0r652eyqljpe6z2iru.jpeg",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/57kzhv3n97x81iasfaxqjw8imwfk2gnq.jpeg",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/we9j5i83d79ho6t057znz7sbv8mvfqyn.jpeg",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/hfh9zk9rgzy4w47vw8rrn5ik9py4bx6p.jpeg",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/7kgycsgjzhux9xvpmmfv6ixx84m188kf.png",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/f036dy2rc1fr1ng5ks0gm3iltrpnqv1b.jpeg",
    "https://palm-dev.d3fau1t.net/pictures/olq4h60m7yaqbprz/pxyd2l1dvn516iaelsa58jk04ithekbl.jpeg",
  ];

  let container: HTMLDivElement;
  let controls: PointerLockControls;
  const scene = new THREE.Scene();

  // 키보드 입력 상태 저장
  // let keyDownTime: { [key: string]: number } = {};
  let keyState: { [key: string]: boolean } = {};


  const onKeyDown = (event: KeyboardEvent) => {
    keyState[event.key] = true;
  };

  const onKeyUp = (event: KeyboardEvent) => {
    keyState[event.key] = false;
  };

  // 충돌감지를 위한 레이케스터 초기화
  const raycaster = new THREE.Raycaster();
  const raycasterDirection = new THREE.Vector3();
  const raycasterOrigin = new THREE.Vector3();

  const updateMovement = () => {
    let walkingSpeed = 0.1; // 이동 속도
    let runningSpeed = 0.5;
    let speed = keyState['Shift'] ? runningSpeed : walkingSpeed;

    // 플레이어의 현재 방향과 위치를 가져옴
    if (!controls) {
      requestAnimationFrame(updateMovement);
      return;
    }
    controls.getDirection(raycasterDirection);
    raycasterOrigin.copy(controls.getObject().position);

    // 레이캐스터를 플레이어의 현재 위치와 방향으로 설정
    raycaster.set(raycasterOrigin, raycasterDirection);

    // 벽과의 교차점 계산
    const intersections = raycaster.intersectObjects(scene.children);

    // 교차점이 있고, 일정 거리(예: 1) 이내에 있다면 이동하지 않음
    if (intersections.length > 0 && intersections[0].distance < 1) {
      speed=0
    }

    if (keyState['w']) controls.moveForward(speed);
    if (keyState['a']) controls.moveRight(-speed);
    if (keyState['s']) controls.moveForward(-speed);
    if (keyState['d']) controls.moveRight(speed);

    requestAnimationFrame(updateMovement);
  }

  onMount(() => {
    // 키보드 입력 이벤트 리스너 등록
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);
    updateMovement();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);


    // 월드 생성 로직
    // 나무장판 텍스처 로드
    const textureLoader = new THREE.TextureLoader();
    const floorTexture = textureLoader.load('/images/wood-floor.jpg'); // 나무장판 텍스처 경로로 변경하세요
    floorTexture.wrapS = THREE.RepeatWrapping;
    floorTexture.wrapT = THREE.RepeatWrapping;
    floorTexture.repeat.set(10, 10); // 텍스처 반복 횟수 조정
    // 바닥 메시 생성
    const floorGeometry = new THREE.PlaneGeometry(50, 50); // 바닥 크기 조정
    const floorMaterial = new THREE.MeshBasicMaterial({ map: floorTexture });
    const floorMesh = new THREE.Mesh(floorGeometry, floorMaterial);
    floorMesh.rotation.x = -Math.PI / 2; // 바닥을 수평으로 회전
    floorMesh.position.y = -0.5; // 바닥 위치 조정
    scene.add(floorMesh);

    // 대리석 벽 텍스처 로드
    const marbleWallTexture = textureLoader.load('/images/marble-pattern.jpg'); // 대리석 벽 텍스처 경로로 변경하세요
    // 대리석 벽 메시 생성
    const wallGeometry = new THREE.PlaneGeometry(50, 20); // 벽 크기 조정
    const wallMaterial = new THREE.MeshBasicMaterial({ map: marbleWallTexture });
    // 바닥이 끝나는 지점에 벽 생성
    const wallMeshFront = new THREE.Mesh(wallGeometry, wallMaterial);
    const wallMeshBack = new THREE.Mesh(wallGeometry, wallMaterial);
    const wallMeshLeft = new THREE.Mesh(wallGeometry, wallMaterial);
    const wallMeshRight = new THREE.Mesh(wallGeometry, wallMaterial);
    wallMeshFront.position.z = -25;
    wallMeshFront.position.y = 9.5;
    wallMeshBack.position.z = 25;
    wallMeshBack.position.y = 9.5;
    // NOTE: 뒤에서 보면 안보임
    wallMeshBack.rotateX(Math.PI);
    wallMeshLeft.position.x = -25;
    wallMeshLeft.position.y = 9.5;
    wallMeshLeft.rotateY(Math.PI / 2);
    wallMeshRight.position.x = 25;
    wallMeshRight.position.y = 9.5;
    wallMeshRight.rotateY(-Math.PI / 2);
    // 추가
    scene.add(wallMeshFront);
    scene.add(wallMeshBack);
    scene.add(wallMeshLeft);
    scene.add(wallMeshRight);

    camera.position.z = 10;
    camera.position.y= 5

    // imageUrls를 하나씩 벽에 붙이기
    let wallLength = 50; // 벽 길이
    let spacing = 7; // 이미지 간격
    let imageWidth = 10;
    let currentWallIndex = 0;

    const walls = ['front', 'back', 'left', 'right']
    const wallUsedLength: { [key: string]: number } = {
      front: 0,
      back: 0,
      left: 0,
      right: 0
    }

    imageUrls.forEach((url, index) => {
      const imageTexture = textureLoader.load(url);
      const imageGeometry = new THREE.PlaneGeometry(imageWidth, imageWidth); // 정사각형 이미지 가정
      const imageMaterial = new THREE.MeshBasicMaterial({ map: imageTexture });
      const imageMesh = new THREE.Mesh(imageGeometry, imageMaterial);

      let currentWall = walls[currentWallIndex % walls.length];
      if (wallUsedLength[currentWall] + imageWidth > wallLength) {
        currentWallIndex++;
        currentWall = walls[currentWallIndex % walls.length];
        // wallUsedLength[currentWall] = 0;
      }
      let positionX = 0, positionZ = 0, rotationY = 0;
      let positionY = 10;

      // 벽에 따른 위치 및 회전 설정
      switch (currentWall) {
        case 'front':
          positionZ = (-wallLength / 2) + 1;
          positionX = wallUsedLength[currentWall] - (wallLength / 2 - imageWidth / 2);
          break;
        case 'back':
          positionZ = (wallLength / 2) - 1;
          positionX = wallUsedLength[currentWall] - (wallLength / 2 - imageWidth / 2);
          rotationY = Math.PI;
          break;
        case 'left':
          positionX = (-wallLength / 2) + 1;
          positionZ = wallUsedLength[currentWall] - (wallLength / 2 - imageWidth / 2);
          rotationY = Math.PI / 2;
          break;
        case 'right':
          positionZ = wallUsedLength[currentWall] - (wallLength / 2 - imageWidth / 2);
          positionX = (wallLength / 2) -1;
          rotationY = -Math.PI / 2;
          break;
      }

      // 이미지 위치 설정
      imageMesh.position.set(positionX, positionY, positionZ);
      // 높이 설정
      imageMesh.rotation.y = rotationY;

      // 벽 사용 길이 업데이트 및 벽 넘어가는 처리
      wallUsedLength[currentWall] += imageWidth + spacing;
      // if (wallUsedLength[currentWall] > wallLength) {
      //   currentWallIndex++; // 다음 벽으로 이동
      //   wallUsedLength[currentWall] = 0; // 다음 벽의 사용 길이 초기화
      // }

      scene.add(imageMesh);
    });



    // 하늘 이미지 로드
    const skyTexture = textureLoader.load('/images/blue-sky.png'); // 하늘 이미지 경로로 변경하세요
    scene.background = skyTexture;

    // 플레이어 컨트롤 초기화
    controls = new PointerLockControls(camera, renderer.domElement);
    scene.add(controls.getObject());

    // 마우스 클릭 시 컨트롤 활성화
    container.addEventListener('click', () => {
      controls.lock();
    });

    // 렌더링 루프
    const animate = () => {
      requestAnimationFrame(animate);
      // 게임 로직 업데이트
      renderer.render(scene, camera);
    };

    animate();
  });
</script>

<div bind:this={container} style="width:100vw; height:100vh;"></div>
